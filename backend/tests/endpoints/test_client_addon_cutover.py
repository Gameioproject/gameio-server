from unittest.mock import AsyncMock, Mock

import pytest
from tests.endpoints.test_catalog import _game

import config
from handler.compat import argosy
from handler.database import db_catalog_handler, db_game_source_handler
from models.game_source import GameHostKind


@pytest.fixture
def source_catalog(monkeypatch):
    monkeypatch.setattr(config, "GAMEIO_CLIENT_ADDONS_ONLY", False)
    db_catalog_handler.upsert_games(
        [
            _game(1074, "Super Mario 64"),
            _game(3475, "Dr. Mario 64"),
            _game(6080, "PaRappa the Rapper", platform_slugs=["psx"]),
        ]
    )
    host = db_game_source_handler.add_host(
        name="Private test source",
        kind=GameHostKind.TORRENT,
        base="private-source",
    )
    host = db_game_source_handler.update_host(host.id, info_hash="a" * 40)
    match = db_catalog_handler.get_game_by_igdb_id(3475)
    db_game_source_handler.upsert_sources(
        host.id,
        [
            dict(
                catalog_game_id=match["game"].id,
                path="private-game.z64",
                filename="private-game.z64",
                platform_slug="n64",
                size=1234,
                md5=None,
                sha1=None,
                region="USA",
                file_index=3,
            )
        ],
    )
    source = db_game_source_handler.get_source_by_path(host.id, "private-game.z64")
    return host, source, argosy.rom_id(match["game"].id, "n64")


@pytest.fixture
def enabled(monkeypatch, source_catalog):
    monkeypatch.setattr(config, "GAMEIO_CLIENT_ADDONS_ONLY", True)
    return source_catalog


@pytest.fixture
def headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}


def test_staged_default_keeps_existing_server_download_metadata(
    client, headers, source_catalog
):
    response = client.get("/api/catalog/3475", headers=headers)
    assert response.status_code == 200
    assert response.json()["owned"] is True
    assert response.json()["sources"][0]["magnet"].startswith(
        "magnet:?xt=urn:btih:" + "a" * 40
    )
    assert (
        client.get("/api/hosts", headers=headers).json()[0]["base"] == "private-source"
    )


@pytest.mark.parametrize(
    "query",
    ["", "?owned=true", "?owned=false", "?owned_platforms=true", "?order_by=added"],
)
def test_catalog_remains_complete_without_source_locators(
    client, headers, enabled, query
):
    response = client.get("/api/catalog" + query, headers=headers)
    assert response.status_code == 200
    page = response.json()
    assert page["total"] == 3
    assert {game["igdb_id"] for game in page["items"]} == {1074, 3475, 6080}
    assert all(
        game["sources"] == [] and game["owned"] is False for game in page["items"]
    )
    assert "private-source" not in response.text
    assert "magnet:" not in response.text
    detail = client.get("/api/catalog/3475", headers=headers).json()
    assert detail["name"] == "Dr. Mario 64"
    assert detail["platform_slugs"] == ["n64"]
    assert detail["sources"] == []
    filters = client.get("/api/catalog/filters", headers=headers).json()
    assert filters["total_games"] == 3
    assert filters["owned_games"] == 0
    assert all(platform["owned_count"] == 0 for platform in filters["platforms"])


def test_compat_roms_keep_catalog_identity_but_no_server_files(
    client, headers, enabled
):
    _, _, rom_id = enabled
    detail = client.get(f"/api/roms/{rom_id}", headers=headers)
    assert detail.status_code == 200
    rom = detail.json()
    assert rom["igdb_id"] == 3475
    assert rom["name"] == "Dr. Mario 64"
    assert rom["files"] == []
    assert rom["has_download"] is False
    assert "private-game" not in detail.text
    page = client.get("/api/roms?owned=true", headers=headers)
    assert page.status_code == 200
    assert len(page.json()["items"]) == 3
    assert all(
        not game["has_download"] and not game["files"] for game in page.json()["items"]
    )
    assert client.get("/api/hosts", headers=headers).json() == []


@pytest.mark.parametrize(
    "method,path",
    [
        (method, path)
        for method in ("GET", "HEAD")
        for path in (
            "/api/catalog/3475/download",
            "/api/catalog/3475/stream",
            "/api/roms/{rom_id}/content/private-game.z64",
        )
    ],
)
def test_downloads_and_proxies_stop_before_resolution(
    client, headers, enabled, monkeypatch, method, path
):
    resolver = AsyncMock(
        side_effect=AssertionError("must not resolve any server source")
    )
    monkeypatch.setattr("endpoints.catalog.resolve_source_url", resolver)
    monkeypatch.setattr("endpoints.compat_argosy.resolve_source_url", resolver)
    response = client.request(
        method, path.format(rom_id=enabled[2]), headers=headers, follow_redirects=False
    )
    assert response.status_code == 410
    resolver.assert_not_called()


@pytest.mark.parametrize(
    "method,path,body",
    [
        (
            "POST",
            "/api/hosts",
            {"name": "New host", "kind": "http", "base": "https://sources.test"},
        ),
        ("PATCH", "/api/hosts/{host_id}", {"enabled": False}),
        ("DELETE", "/api/hosts/{host_id}", None),
        ("POST", "/api/hosts/{host_id}/index", None),
        ("POST", "/api/catalog/3475/sources", {"url": "https://sources.test/game.z64"}),
        ("DELETE", "/api/catalog/sources/{source_id}", None),
    ],
)
def test_host_and_source_mutations_are_disabled_before_lookup_or_enqueue(
    client, headers, enabled, monkeypatch, method, path, body
):
    host, source, _ = enabled
    lookup = Mock(side_effect=AssertionError("must not consult old source locators"))
    enqueue = Mock(side_effect=AssertionError("must not queue server indexing"))
    monkeypatch.setattr("endpoints.hosts._get_host", lookup)
    monkeypatch.setattr("endpoints.hosts.low_prio_queue.enqueue", enqueue)
    response = client.request(
        method,
        path.format(host_id=host.id, source_id=source.id),
        headers=headers,
        json=body,
    )
    assert response.status_code == 410
    lookup.assert_not_called()
    enqueue.assert_not_called()


@pytest.mark.asyncio
async def test_low_level_source_entrypoints_reject_queued_and_direct_work(
    enabled, monkeypatch
):
    from handler.sources.indexer import index_host_files
    from handler.sources.policy import SourceHandlingDisabled
    from handler.sources.resolver import resolve_source_url
    from tasks.manual.index_game_host import index_game_host_task

    host, source, _ = enabled
    with pytest.raises(SourceHandlingDisabled):
        await resolve_source_url(source)
    with pytest.raises(SourceHandlingDisabled):
        index_host_files(host, [])
    lookup = Mock(
        side_effect=AssertionError("queued task must stop before reading host")
    )
    monkeypatch.setattr(db_game_source_handler, "get_host", lookup)
    with pytest.raises(SourceHandlingDisabled):
        await index_game_host_task.run(host.id)
    lookup.assert_not_called()


def test_generic_task_runner_and_task_list_cannot_reenable_host_indexing(
    client, headers, enabled, monkeypatch
):
    enqueue = Mock(side_effect=AssertionError("must not queue source handling"))
    monkeypatch.setattr("endpoints.tasks.low_prio_queue.enqueue", enqueue)
    response = client.post(
        "/api/tasks/run/index_game_host",
        headers=headers,
        json={"host_id": enabled[0].id},
    )
    assert response.status_code == 410
    enqueue.assert_not_called()
    tasks = client.get("/api/tasks", headers=headers)
    assert tasks.status_code == 200
    assert all(task["name"] != "index_game_host" for task in tasks.json()["manual"])
