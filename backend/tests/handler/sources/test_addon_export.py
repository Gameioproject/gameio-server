import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import Session

import config
from handler.sources import addon_export
from handler.sources.addon_export import (
    ExportSource,
    build_snapshot,
    shard_for,
    write_snapshot,
)
from models.game_source import GameHostKind


def source(**overrides) -> ExportSource:
    return replace(
        ExportSource(
            igdb_id=7344,
            platform_slug="snes",
            kind=GameHostKind.INTERNET_ARCHIVE,
            base="test-collection",
            path="Games/Test Game (USA).zip",
            filename="Test Game (USA).zip",
            size=1234,
            md5="A" * 32,
            sha1="B" * 40,
            region="USA",
        ),
        **overrides,
    )


def snapshot(rows, **overrides):
    options = {
        "addon_id": "org.gameio.test",
        "name": "Test sources",
        "version": "2026-09-14",
        "base_url": "https://sources.example.org/v1",
    }
    return build_snapshot(rows, **(options | overrides))


def entry(files, key="7344:snes"):
    return json.loads(files[f"{shard_for(key)}.json"])["entries"][key][0]


def test_snapshot_is_portable_bounded_and_deterministic():
    rows = [source(), source(igdb_id=9, platform_slug="n64")]
    files = snapshot(rows)
    assert files == snapshot(list(reversed(rows)))
    assert len(files) == 257
    manifest = json.loads(files["manifest.json"])
    assert manifest == {
        "schemaVersion": 1,
        "id": "org.gameio.test",
        "name": "Test sources",
        "version": "2026-09-14",
        "adapter": "catalog-shards-v1",
        "lookup": {
            "key": "igdbId:platformSlug",
            "partition": "sha256-prefix-2",
            "urlTemplate": "https://sources.example.org/v1/{shard}.json",
        },
        "allowedHosts": ["sources.example.org"],
    }
    assert len(files["manifest.json"]) < addon_export.MANIFEST_MAX_BYTES
    exported = entry(files)
    assert exported["kind"] == "internet_archive"
    assert exported["locator"] == {
        "item": "test-collection",
        "path": "Games/Test Game (USA).zip",
    }
    assert exported["size"] == 1234
    assert exported["md5"] == "a" * 32
    assert exported["sha1"] == "b" * 40
    assert set(exported) == {
        "id",
        "kind",
        "locator",
        "filename",
        "size",
        "md5",
        "sha1",
        "region",
    }
    assert shard_for("7344:snes") == hashlib.sha256(b"7344:snes").hexdigest()[:2]
    assert any(
        json.loads(content)["entries"] == {}
        for filename, content in files.items()
        if filename != "manifest.json"
    )


@pytest.mark.parametrize("client_only", [False, True])
def test_database_export_reads_enabled_sources_using_igdb_identity(
    monkeypatch, client_only
):
    monkeypatch.setattr(config, "GAMEIO_CLIENT_ADDONS_ONLY", client_only)
    from handler import database  # noqa: F401
    from models.catalog import CatalogGame
    from models.game_source import GameHost, GameSource

    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        for model in (CatalogGame, GameHost, GameSource):
            model.metadata.tables[model.__tablename__].create(connection)
        connection.execute(
            insert(CatalogGame), {"id": 1, "igdb_id": 7344, "name": "Test"}
        )
        connection.execute(
            insert(GameHost),
            [
                {
                    "id": 1,
                    "name": "Enabled",
                    "base": "collection",
                    "kind": GameHostKind.INTERNET_ARCHIVE,
                    "enabled": True,
                },
                {
                    "id": 2,
                    "name": "Disabled",
                    "base": "collection",
                    "kind": GameHostKind.INTERNET_ARCHIVE,
                    "enabled": False,
                },
            ],
        )
        connection.execute(
            insert(GameSource),
            [
                {
                    "catalog_game_id": 1,
                    "host_id": host_id,
                    "path": "Game.zip",
                    "filename": "Game.zip",
                    "platform_slug": "snes",
                }
                for host_id in (1, 2)
            ],
        )
    with Session(engine) as session:
        exported = addon_export._read_enabled_sources(session)
    engine.dispose()
    assert len(exported) == 1
    assert exported[0].igdb_id == 7344
    assert exported[0].kind == GameHostKind.INTERNET_ARCHIVE


def test_identity_does_not_change_with_catalog_id_or_file_metadata():
    initial = entry(snapshot([source()]))["id"]
    modified = entry(
        snapshot([source(igdb_id=9, size=456, region="Europe")]), "9:snes"
    )["id"]
    assert initial == modified
    assert initial != entry(snapshot([source(path="Another.zip")]))["id"]


def test_torrent_contains_only_portable_locator():
    result = entry(
        snapshot(
            [
                source(
                    kind=GameHostKind.TORRENT,
                    base="https://private.example?token=do-not-export",
                    info_hash="F" * 40,
                    file_index=0,
                )
            ]
        )
    )
    assert result["locator"] == {
        "infoHash": "f" * 40,
        "fileIndex": 0,
        "path": "Games/Test Game (USA).zip",
    }
    assert "private.example" not in json.dumps(result)
    assert "token" not in json.dumps(result)


def test_http_encodes_path_and_adds_only_its_host():
    files = snapshot(
        [source(kind=GameHostKind.HTTP, base="https://files.example.org/roms")]
    )
    assert entry(files)["locator"] == {
        "url": "https://files.example.org/roms/Games/Test%20Game%20%28USA%29.zip"
    }
    assert json.loads(files["manifest.json"])["allowedHosts"] == [
        "files.example.org",
        "sources.example.org",
    ]


@pytest.mark.parametrize(
    "url",
    [
        "http://files.example.org",
        "https://user:password@files.example.org",
        "https://files.example.org?token=secret",
        "https://files.example.org?expires=9999",
        "https://files.example.org#fragment",
        "https://files.example.org:invalid",
        "https://files.example.org\n",
    ],
)
def test_export_refuses_credential_or_ephemeral_urls(url):
    with pytest.raises(ValueError):
        snapshot([], base_url=url)
    with pytest.raises(ValueError):
        snapshot([source(kind=GameHostKind.HTTP, base=url)])


@pytest.mark.parametrize(
    "changes",
    [
        {"path": "../secret.zip"},
        {"path": "/absolute.zip"},
        {"path": "bad\\path.zip"},
        {"path": "bad\npath.zip"},
        {"filename": "folder/file.zip"},
        {"filename": ".."},
        {"size": -1},
        {"md5": "not-a-checksum"},
        {"sha1": "a" * 39},
        {"igdb_id": 0},
        {"platform_slug": "../snes"},
        {"base": "../archive"},
        {"kind": GameHostKind.TORRENT, "info_hash": "a" * 39, "file_index": 1},
        {"kind": GameHostKind.TORRENT, "info_hash": "a" * 40},
        {"kind": GameHostKind.TORRENT, "info_hash": "a" * 40, "file_index": -1},
    ],
)
def test_export_rejects_unusable_sources(changes):
    with pytest.raises(ValueError):
        snapshot([source(**changes)])


def test_limits_fail_before_writing_partial_data(monkeypatch):
    monkeypatch.setattr(addon_export, "SOURCES_MAX_PER_KEY", 1)
    with pytest.raises(ValueError, match="sources"):
        snapshot([source(), source(path="Other.zip")])
    monkeypatch.setattr(addon_export, "SHARD_MAX_KEYS", 0)
    with pytest.raises(ValueError, match="mapped games"):
        snapshot([source()])
    monkeypatch.setattr(addon_export, "SHARD_MAX_KEYS", 1000)
    monkeypatch.setattr(addon_export, "SHARD_MAX_BYTES", 10)
    with pytest.raises(ValueError, match="bytes"):
        snapshot([])


def test_duplicate_rows_are_not_duplicate_sources():
    files = snapshot([source(), source()])
    assert (
        len(json.loads(files[f"{shard_for('7344:snes')}.json"])["entries"]["7344:snes"])
        == 1
    )


def test_same_locator_with_conflicting_metadata_is_not_two_sources():
    with pytest.raises(ValueError, match="conflicting metadata"):
        snapshot([source(), source(size=10)])


def test_unknown_zero_size_is_omitted():
    assert "size" not in entry(snapshot([source(size=0)]))


def test_failed_write_removes_staging_directory(tmp_path, monkeypatch):
    def fail_write(self, content):
        raise OSError("Disk full")

    monkeypatch.setattr(Path, "write_bytes", fail_write)
    with pytest.raises(OSError, match="Disk full"):
        write_snapshot(tmp_path / "version", snapshot([]))
    assert list(tmp_path.iterdir()) == []


def test_write_preserves_existing_export(tmp_path):
    target = tmp_path / "new-version"
    files = snapshot([source()])
    write_snapshot(target, files)
    assert (target / "manifest.json").read_bytes() == files["manifest.json"]
    with pytest.raises(ValueError, match="already exists"):
        write_snapshot(target, snapshot([]))
    assert (target / "manifest.json").read_bytes() == files["manifest.json"]
    assert sorted(path.name for path in tmp_path.iterdir()) == ["new-version"]
