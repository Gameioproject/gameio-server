"""Read-only client for the Internet Archive metadata API."""

import re
from typing import Final, TypedDict
from urllib.parse import unquote, urlsplit

from utils.context import ctx_httpx_client

IA_METADATA_URL: Final = "https://archive.org/metadata"
IA_REQUEST_TIMEOUT: Final = 60
IA_HOSTS: Final = frozenset({"archive.org", "www.archive.org"})
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class IAItemMeta(TypedDict):
    """The parts of an item's metadata that hint at what it holds."""

    title: str
    description: str
    subject: list[str]


def parse_item_identifier(value: str) -> str:
    """Accept a bare identifier or any archive.org item link and return the identifier."""
    value = value.strip()
    parts = urlsplit(value)
    if parts.scheme in ("http", "https"):
        if parts.netloc.lower() not in IA_HOSTS:
            raise ValueError("Not an archive.org link")
        segments = [s for s in unquote(parts.path).split("/") if s]
        if len(segments) < 2 or segments[0] not in ("details", "download", "metadata"):
            raise ValueError("Expected an archive.org/details/<item> link")
        value = segments[1]
    if not _IDENTIFIER.match(value):
        raise ValueError("Not a valid Internet Archive item identifier")
    return value


class IAFile(TypedDict):
    """One file of an item, as the metadata API lists it (only the keys used here)."""

    name: str
    source: str
    size: int | None
    md5: str | None
    sha1: str | None


def _to_int(value: object) -> int | None:
    """IA reports sizes as strings."""
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _to_str_list(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value]
    return []


async def fetch_item_metadata(identifier: str) -> IAItemMeta:
    """The item's title, description and tags; empty strings when unavailable."""
    client = ctx_httpx_client.get()
    response = await client.get(
        f"{IA_METADATA_URL}/{identifier}/metadata", timeout=IA_REQUEST_TIMEOUT
    )
    response.raise_for_status()
    payload = response.json()
    meta = payload.get("result") if isinstance(payload, dict) else None
    if not isinstance(meta, dict):
        meta = {}
    return {
        "title": str(meta.get("title") or ""),
        "description": " ".join(_to_str_list(meta.get("description"))),
        "subject": _to_str_list(meta.get("subject")),
    }


async def fetch_item_files(identifier: str) -> list[IAFile]:
    """List the original (non-derivative) files of an Internet Archive item."""
    client = ctx_httpx_client.get()
    response = await client.get(
        f"{IA_METADATA_URL}/{identifier}/files", timeout=IA_REQUEST_TIMEOUT
    )
    response.raise_for_status()
    payload = response.json()
    files = payload.get("result") if isinstance(payload, dict) else None
    if not isinstance(files, list):
        return []
    return [
        {
            "name": str(entry["name"]),
            "source": str(entry.get("source", "original")),
            "size": _to_int(entry.get("size")),
            "md5": entry.get("md5"),
            "sha1": entry.get("sha1"),
        }
        for entry in files
        if isinstance(entry, dict) and entry.get("name")
    ]
