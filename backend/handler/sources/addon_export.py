"""Export a portable, bounded snapshot of existing catalog source mappings."""

import hashlib
import json
import re
import shutil
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.catalog import CatalogGame
from models.game_source import (
    SOURCE_FILENAME_MAX_LENGTH,
    SOURCE_PATH_MAX_LENGTH,
    GameHost,
    GameHostKind,
    GameSource,
)

SCHEMA_VERSION = 1
MANIFEST_MAX_BYTES = 64 * 1024
SHARD_MAX_BYTES = 1024 * 1024
SHARD_MAX_KEYS = 1000
SOURCES_MAX_PER_KEY = 200
SHARD_COUNT = 256
_SLUG = re.compile(r"[a-z0-9][a-z0-9-]{0,99}")
_ADDON_ID = re.compile(r"[a-z0-9]+(?:[._-][a-z0-9]+)*")
_ITEM = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")


@dataclass(frozen=True)
class ExportSource:
    igdb_id: int
    platform_slug: str
    kind: GameHostKind
    base: str
    path: str
    filename: str
    info_hash: str | None = None
    file_index: int | None = None
    size: int | None = None
    md5: str | None = None
    sha1: str | None = None
    region: str | None = None


def read_enabled_sources() -> list[ExportSource]:
    """Read only enabled mappings without resolving links or loading credentials."""
    # Register all models before loading the session decorator.
    # isort: off
    from handler import database  # noqa: F401
    from decorators.database import begin_session

    # isort: on

    return begin_session(_read_enabled_sources)()


def _read_enabled_sources(session: Session) -> list[ExportSource]:
    rows = session.execute(
        select(
            CatalogGame.igdb_id,
            GameSource.platform_slug,
            GameHost.kind,
            GameHost.base,
            GameSource.path,
            GameSource.filename,
            GameHost.info_hash,
            GameSource.file_index,
            GameSource.size,
            GameSource.md5,
            GameSource.sha1,
            GameSource.region,
        )
        .join(GameSource, GameSource.catalog_game_id == CatalogGame.id)
        .join(GameHost, GameHost.id == GameSource.host_id)
        .where(GameHost.enabled.is_(True))
    ).mappings()
    return [ExportSource(**row) for row in rows]


def lookup_key(igdb_id: int, platform_slug: str) -> str:
    if igdb_id <= 0 or not _SLUG.fullmatch(platform_slug):
        raise ValueError("A mapping needs a positive IGDB id and platform slug")
    return f"{igdb_id}:{platform_slug}"


def shard_for(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:2]


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _https_host(value: str) -> str:
    parts = urlsplit(value)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or parts.query
        or parts.fragment
        or any(ord(char) < 33 for char in value)
    ):
        raise ValueError(
            "Export URLs must be HTTPS without credentials, queries or fragments"
        )
    try:
        _ = parts.port
    except ValueError as exc:
        raise ValueError("Invalid export URL port") from exc
    return parts.hostname.lower()


def _relative_path(value: str) -> None:
    if (
        not value
        or len(value) > SOURCE_PATH_MAX_LENGTH
        or "\\" in value
        or any(part in ("", ".", "..") for part in value.split("/"))
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        raise ValueError("Source paths must be relative file paths without traversal")


def _source_entry(row: ExportSource) -> tuple[dict[str, Any], str | None]:
    _relative_path(row.path)
    _relative_path(row.filename)
    if "/" in row.filename or len(row.filename) > SOURCE_FILENAME_MAX_LENGTH:
        raise ValueError("Source filename must be a file name, not a path")
    download_host = None
    locator: dict[str, Any]
    if row.kind == GameHostKind.INTERNET_ARCHIVE:
        if not _ITEM.fullmatch(row.base) or len(row.base) > 200:
            raise ValueError("Internet Archive source needs a plain item identifier")
        locator = {"item": row.base, "path": row.path}
    elif row.kind == GameHostKind.HTTP:
        download_host = _https_host(row.base)
        locator = {"url": f"{row.base.rstrip('/')}/{quote(row.path, safe='/')}"}
    elif row.kind == GameHostKind.TORRENT:
        if (
            row.info_hash is None
            or not re.fullmatch(r"[a-fA-F0-9]{40}", row.info_hash)
            or row.file_index is None
            or row.file_index < 0
        ):
            raise ValueError(
                "Torrent source needs its indexed info hash and file index"
            )
        locator = {
            "infoHash": row.info_hash.lower(),
            "fileIndex": row.file_index,
            "path": row.path,
        }
    else:
        raise ValueError("Unsupported source kind")
    identity = {"kind": str(row.kind), "locator": locator}
    entry: dict[str, Any] = {
        "id": hashlib.sha256(_json_bytes(identity)).hexdigest(),
        **identity,
        "filename": row.filename,
    }
    for field, value in (
        ("size", row.size or None),
        ("md5", row.md5),
        ("sha1", row.sha1),
        ("region", row.region),
    ):
        if value is not None:
            entry[field] = value
    if row.size is not None and row.size < 0:
        raise ValueError("Source size cannot be negative")
    for field, length in (("md5", 32), ("sha1", 40)):
        checksum = entry.get(field)
        if checksum is not None:
            if not re.fullmatch(rf"[a-fA-F0-9]{{{length}}}", checksum):
                raise ValueError(f"Invalid source {field} checksum")
            entry[field] = checksum.lower()
    return entry, download_host


def build_snapshot(
    sources: Sequence[ExportSource],
    *,
    addon_id: str,
    name: str,
    version: str,
    base_url: str,
) -> dict[str, bytes]:
    """Validate the complete snapshot before creating any output files."""
    if not _ADDON_ID.fullmatch(addon_id) or len(addon_id) > 100:
        raise ValueError(
            "Add-on id must use lowercase letters, digits, dots, hyphens or underscores"
        )
    if not name.strip() or len(name) > 100 or not version.strip() or len(version) > 100:
        raise ValueError(
            "Add-on name and version are required and must fit their limits"
        )
    allowed_hosts = {_https_host(base_url)}
    entries: dict[str, dict[str, list[dict[str, Any]]]] = {
        f"{index:02x}": {} for index in range(SHARD_COUNT)
    }
    for row in sources:
        key = lookup_key(row.igdb_id, row.platform_slug)
        entry, download_host = _source_entry(row)
        if download_host:
            allowed_hosts.add(download_host)
        group = entries[shard_for(key)].setdefault(key, [])
        if any(
            existing["id"] == entry["id"] and existing != entry for existing in group
        ):
            raise ValueError(
                f"Mapping {key} has conflicting metadata for the same locator"
            )
        if entry not in group:
            group.append(entry)
        if len(group) > SOURCES_MAX_PER_KEY:
            raise ValueError(f"Mapping {key} exceeds {SOURCES_MAX_PER_KEY} sources")
    files: dict[str, bytes] = {}
    for shard, shard_entries in entries.items():
        if len(shard_entries) > SHARD_MAX_KEYS:
            raise ValueError(f"Shard {shard} exceeds {SHARD_MAX_KEYS} mapped games")
        for group in shard_entries.values():
            group.sort(key=lambda source: source["id"])
        content = _json_bytes(
            {"schemaVersion": SCHEMA_VERSION, "entries": shard_entries}
        )
        if len(content) > SHARD_MAX_BYTES:
            raise ValueError(f"Shard {shard} exceeds {SHARD_MAX_BYTES} bytes")
        files[f"{shard}.json"] = content
    manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "id": addon_id,
        "name": name.strip(),
        "version": version.strip(),
        "adapter": "catalog-shards-v1",
        "lookup": {
            "key": "igdbId:platformSlug",
            "partition": "sha256-prefix-2",
            "urlTemplate": f"{base_url.rstrip('/')}/{{shard}}.json",
        },
        "allowedHosts": sorted(allowed_hosts),
    }
    if len(allowed_hosts) > 64:
        raise ValueError("Manifest exceeds 64 allowed hosts")
    content = _json_bytes(manifest)
    if len(content) > MANIFEST_MAX_BYTES:
        raise ValueError(f"Manifest exceeds {MANIFEST_MAX_BYTES} bytes")
    files["manifest.json"] = content
    return files


def write_snapshot(output: Path, files: dict[str, bytes]) -> None:
    """Write into a new directory atomically, preserving any existing export."""
    if output.exists():
        raise ValueError(
            "Output directory already exists; choose a new version directory"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent))
    try:
        for filename, content in files.items():
            (staging / filename).write_bytes(content)
        staging.rename(output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
