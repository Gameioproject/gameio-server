from contextlib import asynccontextmanager

import pytest
from fastapi import status

from handler.database import (
    db_catalog_handler,
    db_collection_handler,
    db_game_source_handler,
)
from handler.database.catalog_handler import CatalogGameInput
from models.collection import Collection
from models.game_source import GameHost, GameHostKind, GameSource

OWNED_PATH = "n64/Dr. Mario 64 (USA).z64"


def _game(igdb_id: int, name: str, **overrides) -> CatalogGameInput:
    data: CatalogGameInput = {
        "igdb_id": igdb_id,
        "name": name,
        "slug": name.lower().replace(" ", "-"),
        "summary": f"{name} summary",
        "release_year": 1996,
        "first_release_date": 835660800,
        "cover_image_id": "co1abc",
        "screenshot_image_ids": ["sc1", "sc2"],
        "genres": ["Platform"],
        "platform_slugs": ["n64"],
        "rating": 90.0,
        "rating_count": 100,
        "youtube_video_id": "dQw4w9WgXcQ",
        "igdb_url": f"https://www.igdb.com/games/{name}",
        "source_updated_at": 1700000000,
    }
    data.update(overrides)  # type: ignore[typeddict-item]
    return data


@pytest.fixture
def catalog_games() -> list[CatalogGameInput]:
    games = [
        _game(1074, "Super Mario 64"),
        _game(3475, "Dr. Mario 64", genres=["Puzzle"], rating=75.0, rating_count=20),
        _game(
            6080,
            "PaRappa the Rapper",
            platform_slugs=["psx"],
            genres=["Music"],
            rating=None,
            rating_count=0,
            release_year=1997,
        ),
    ]
    db_catalog_handler.upsert_games(games)
    return games


@pytest.fixture
def ia_host() -> GameHost:
    return db_game_source_handler.add_host(
        name="My N64 item",
        kind=GameHostKind.INTERNET_ARCHIVE,
        base="my-n64-roms",
    )


@pytest.fixture
def owned_source(catalog_games, ia_host: GameHost) -> GameSource:
    match = db_catalog_handler.get_game_by_igdb_id(3475)
    assert match is not None
    db_game_source_handler.upsert_sources(
        ia_host.id,
        [
            {
                "catalog_game_id": match["game"].id,
                "path": OWNED_PATH,
                "filename": "Dr. Mario 64 (USA).z64",
                "platform_slug": "n64",
                "size": 12582912,
                "md5": "a" * 32,
                "sha1": "b" * 40,
                "region": "USA",
            }
        ],
    )
    source = db_game_source_handler.get_source_by_path(ia_host.id, OWNED_PATH)
    assert source is not None
    return source


class TestCatalogEndpoints:
    def test_list_requires_auth(self, client, catalog_games):
        response = client.get("/api/catalog")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_orders_by_rating_with_nulls_last(
        self, client, access_token: str, catalog_games
    ):
        response = client.get(
            "/api/catalog", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["total"] == 3
        assert body["limit"] == 50
        assert body["offset"] == 0
        assert [g["name"] for g in body["items"]] == [
            "Super Mario 64",
            "Dr. Mario 64",
            "PaRappa the Rapper",
        ]
        game = body["items"][0]
        assert game["igdb_id"] == 1074
        assert game["url_cover"] == (
            "https://images.igdb.com/igdb/image/upload/t_1080p/co1abc.jpg"
        )
        assert game["url_cover_small"] == (
            "https://images.igdb.com/igdb/image/upload/t_cover_big/co1abc.jpg"
        )
        assert game["url_screenshots"] == [
            "https://images.igdb.com/igdb/image/upload/t_720p/sc1.jpg",
            "https://images.igdb.com/igdb/image/upload/t_720p/sc2.jpg",
        ]
        assert game["genres"] == ["Platform"]
        assert game["platform_slugs"] == ["n64"]
        assert game["owned"] is False
        assert game["sources"] == []

    def test_owned_state(
        self, client, access_token: str, catalog_games, owned_source: GameSource
    ):
        response = client.get(
            "/api/catalog?order_by=name&order_dir=asc",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        by_igdb = {g["igdb_id"]: g for g in response.json()["items"]}

        assert by_igdb[3475]["owned"] is True
        assert by_igdb[3475]["sources"] == [
            {
                "id": owned_source.id,
                "host_id": owned_source.host_id,
                "host_name": "My N64 item",
                "platform_slug": "n64",
                "filename": "Dr. Mario 64 (USA).z64",
                "size": 12582912,
                "md5": "a" * 32,
                "sha1": "b" * 40,
                "region": "USA",
            }
        ]
        assert by_igdb[1074]["owned"] is False
        assert by_igdb[1074]["sources"] == []
        assert by_igdb[6080]["owned"] is False

    def test_disabled_host_does_not_count_as_owned(
        self, client, access_token: str, owned_source: GameSource
    ):
        db_game_source_handler.add_host(
            name="Off", kind=GameHostKind.HTTP, base="https://x.test", enabled=False
        )
        hosts = db_game_source_handler.get_hosts()
        off_host = next(h for h in hosts if h.name == "Off")
        db_game_source_handler.upsert_sources(
            off_host.id,
            [
                {
                    "catalog_game_id": owned_source.catalog_game_id,
                    "path": "dr-mario.zip",
                    "filename": "dr-mario.zip",
                    "platform_slug": "n64",
                    "size": None,
                    "md5": None,
                    "sha1": None,
                    "region": None,
                }
            ],
        )
        response = client.get(
            "/api/catalog/3475", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert [s["host_name"] for s in response.json()["sources"]] == ["My N64 item"]

    @pytest.mark.parametrize(
        ("query", "expected_names"),
        [
            ("search=mario", ["Dr. Mario 64", "Super Mario 64"]),
            ("search=mario+dr", ["Dr. Mario 64"]),
            ("platform_slug=psx", ["PaRappa the Rapper"]),
            ("exclude_platform=n64", ["PaRappa the Rapper"]),
            ("exclude_platform=n64&exclude_platform=psx", []),
            ("owned=true&exclude_platform=n64", []),
            ("owned=false&exclude_platform=n64", ["PaRappa the Rapper"]),
            ("genre=Puzzle", ["Dr. Mario 64"]),
            ("min_rating=80", ["Super Mario 64"]),
            ("year_from=1997", ["PaRappa the Rapper"]),
            ("year_to=1996", ["Dr. Mario 64", "Super Mario 64"]),
            ("owned=true", ["Dr. Mario 64"]),
            ("owned=false", ["PaRappa the Rapper", "Super Mario 64"]),
            ("owned_platforms=true", ["Dr. Mario 64", "Super Mario 64"]),
            ("owned_platforms=true&owned=false", ["Super Mario 64"]),
        ],
    )
    def test_filters(
        self,
        client,
        access_token: str,
        catalog_games,
        owned_source: GameSource,
        query: str,
        expected_names: list[str],
    ):
        response = client.get(
            f"/api/catalog?order_by=name&order_dir=asc&{query}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert [g["name"] for g in body["items"]] == expected_names
        assert body["total"] == len(expected_names)

    def test_pagination(self, client, access_token: str, catalog_games):
        response = client.get(
            "/api/catalog?order_by=name&order_dir=asc&limit=2&offset=1",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["total"] == 3
        assert body["limit"] == 2
        assert body["offset"] == 1
        assert [g["name"] for g in body["items"]] == [
            "PaRappa the Rapper",
            "Super Mario 64",
        ]

    def test_get_game(
        self, client, access_token: str, catalog_games, owned_source: GameSource
    ):
        response = client.get(
            "/api/catalog/3475", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["name"] == "Dr. Mario 64"
        assert body["summary"] == "Dr. Mario 64 summary"
        assert body["owned"] is True
        assert body["sources"][0]["id"] == owned_source.id

    def test_favorites_and_collections(
        self, client, access_token: str, catalog_games, admin_user
    ):
        headers = {"Authorization": f"Bearer {access_token}"}
        # Favorites are created on first use.
        response = client.post(
            "/api/collections/favorites/games",
            headers=headers,
            json={"igdb_ids": [1074]},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_favorite"] is True
        assert response.json()["game_igdb_ids"] == [1074]
        assert response.json()["game_count"] == 1
        assert response.json()["url_covers"] == [
            "https://images.igdb.com/igdb/image/upload/t_cover_big/co1abc.jpg"
        ]

        game = client.get("/api/catalog/1074", headers=headers).json()
        assert game["is_favorite"] is True
        assert (
            client.get("/api/catalog/3475", headers=headers).json()["is_favorite"]
            is False
        )

        page = client.get("/api/catalog?favorite=true", headers=headers).json()
        assert [g["name"] for g in page["items"]] == ["Super Mario 64"]

        # A regular collection with two games, filtered through the catalog.
        collection = db_collection_handler.add_collection(
            Collection(name="Mario", description="", user_id=admin_user.id)
        )
        response = client.post(
            f"/api/collections/{collection.id}/games",
            headers=headers,
            json={"igdb_ids": [1074, 3475, 999999]},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["game_igdb_ids"] == [1074, 3475]
        page = client.get(
            f"/api/catalog?collection_id={collection.id}&order_by=name&order_dir=asc",
            headers=headers,
        ).json()
        assert [g["name"] for g in page["items"]] == ["Dr. Mario 64", "Super Mario 64"]

        response = client.request(
            "DELETE",
            f"/api/collections/{collection.id}/games",
            headers=headers,
            json={"igdb_ids": [1074]},
        )
        assert response.json()["game_igdb_ids"] == [3475]

        response = client.request(
            "DELETE",
            "/api/collections/favorites/games",
            headers=headers,
            json={"igdb_ids": [1074]},
        )
        assert response.json()["game_igdb_ids"] == []
        assert (
            client.get("/api/catalog?favorite=true", headers=headers).json()["total"]
            == 0
        )

    def test_collection_games_require_ownership(
        self, client, viewer_access_token: str, catalog_games, admin_user
    ):
        collection = db_collection_handler.add_collection(
            Collection(name="Admin only", description="", user_id=admin_user.id)
        )
        response = client.post(
            f"/api/collections/{collection.id}/games",
            headers={"Authorization": f"Bearer {viewer_access_token}"},
            json={"igdb_ids": [1074]},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_ownership_is_per_platform(
        self, client, access_token: str, owned_source: GameSource, ia_host: GameHost
    ):
        """Dr. Mario 64 is listed for n64 and psx but its source is an n64 file."""
        match = db_catalog_handler.get_game_by_igdb_id(3475)
        assert match is not None
        db_catalog_handler.upsert_games(
            [
                _game(
                    3475,
                    "Dr. Mario 64",
                    platform_slugs=["n64", "psx"],
                    genres=["Puzzle"],
                )
            ]
        )
        headers = {"Authorization": f"Bearer {access_token}"}
        n64 = client.get(
            "/api/catalog?owned=true&platform_slug=n64", headers=headers
        ).json()
        psx = client.get(
            "/api/catalog?owned=true&platform_slug=psx", headers=headers
        ).json()
        assert [g["name"] for g in n64["items"]] == ["Dr. Mario 64"]
        assert psx["items"] == []
        facets = client.get("/api/catalog/filters", headers=headers).json()
        counts = {p["slug"]: p["owned_count"] for p in facets["platforms"]}
        assert counts == {"n64": 1, "psx": 0}

    def test_order_by_added(self, client, access_token: str, owned_source: GameSource):
        response = client.get(
            "/api/catalog?order_by=added&order_dir=desc",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        names = [g["name"] for g in response.json()["items"]]
        assert names[0] == "Dr. Mario 64"
        assert len(names) == 3

    def test_download_redirects_to_host(
        self, client, access_token: str, owned_source: GameSource
    ):
        response = client.get(
            "/api/catalog/3475/download",
            headers={"Authorization": f"Bearer {access_token}"},
            follow_redirects=False,
        )
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == (
            "https://archive.org/download/my-n64-roms/n64/Dr.%20Mario%2064%20%28USA%29.z64"
        )
        assert response.headers["x-source-filename"] == "Dr. Mario 64 (USA).z64"
        assert response.headers["x-source-size"] == "12582912"
        assert response.headers["x-source-md5"] == "a" * 32
        assert response.headers["x-source-sha1"] == "b" * 40

    def test_download_head_redirects_too(
        self, client, access_token: str, owned_source: GameSource
    ):
        response = client.head(
            "/api/catalog/3475/download",
            headers={"Authorization": f"Bearer {access_token}"},
            follow_redirects=False,
        )
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"].startswith("https://archive.org/download/")

    def test_stream_relays_host_bytes(
        self, client, access_token: str, owned_source: GameSource, monkeypatch
    ):
        calls: list[dict] = []

        class FakeResponse:
            status_code = 206
            headers = {
                "content-length": "4",
                "content-range": "bytes 0-3/12582912",
                "accept-ranges": "bytes",
                "x-upstream-only": "dropped",
            }

            async def aiter_bytes(self, chunk_size: int):
                yield b"RO"
                yield b"MM"

        class FakeClient:
            @asynccontextmanager
            async def stream(self, method, url, **kwargs):
                calls.append({"method": method, "url": url, **kwargs})
                yield FakeResponse()

        class FakeVar:
            def get(self):
                return FakeClient()

        monkeypatch.setattr("endpoints.catalog.ctx_httpx_client", FakeVar())

        response = client.get(
            "/api/catalog/3475/stream",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Range": "bytes=0-3",
            },
        )
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT
        assert response.content == b"ROMM"
        assert response.headers["content-range"] == "bytes 0-3/12582912"
        assert response.headers["accept-ranges"] == "bytes"
        assert "x-upstream-only" not in response.headers
        assert response.headers["content-disposition"].endswith(
            '"Dr. Mario 64 (USA).z64"'
        )
        assert calls[0]["method"] == "GET"
        assert calls[0]["url"].startswith("https://archive.org/download/my-n64-roms/")
        assert calls[0]["headers"] == {"Range": "bytes=0-3"}
        assert calls[0]["follow_redirects"] is True

        response = client.head(
            "/api/catalog/3475/stream",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_206_PARTIAL_CONTENT
        assert response.content == b""
        assert calls[1]["method"] == "HEAD"

    def test_stream_not_owned(self, client, access_token: str, catalog_games):
        response = client.get(
            "/api/catalog/1074/stream",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_download_unknown_source_id(
        self, client, access_token: str, owned_source: GameSource
    ):
        response = client.get(
            "/api/catalog/3475/download?source_id=999999",
            headers={"Authorization": f"Bearer {access_token}"},
            follow_redirects=False,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_download_not_owned(self, client, access_token: str, catalog_games):
        response = client.get(
            "/api/catalog/1074/download",
            headers={"Authorization": f"Bearer {access_token}"},
            follow_redirects=False,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_and_delete_source(
        self, client, access_token: str, catalog_games, ia_host: GameHost
    ):
        response = client.post(
            "/api/catalog/1074/sources",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "host_id": ia_host.id,
                "path": "n64/Super Mario 64 (USA).z64",
                "platform_slug": "n64",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        source = response.json()
        assert source["filename"] == "Super Mario 64 (USA).z64"
        assert source["host_name"] == "My N64 item"

        game = client.get(
            "/api/catalog/1074", headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        assert game["owned"] is True

        response = client.delete(
            f"/api/catalog/sources/{source['id']}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        game = client.get(
            "/api/catalog/1074", headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        assert game["owned"] is False

    @pytest.mark.parametrize(
        ("url", "kind", "base", "path"),
        [
            (
                "https://archive.org/download/my-set/n64/Super%20Mario%2064%20(USA).z64",
                "internet_archive",
                "my-set",
                "n64/Super Mario 64 (USA).z64",
            ),
            (
                "https://files.example.test/roms/n64/mario.zip",
                "http",
                "https://files.example.test",
                "roms/n64/mario.zip",
            ),
        ],
    )
    def test_add_source_by_direct_link_creates_host(
        self,
        client,
        access_token: str,
        catalog_games,
        url: str,
        kind: str,
        base: str,
        path: str,
    ):
        response = client.post(
            "/api/catalog/1074/sources",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"url": url},
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        source = response.json()
        assert source["platform_slug"] == "n64"
        assert source["filename"] == path.rsplit("/", 1)[-1]
        hosts = db_game_source_handler.get_hosts()
        assert [(h.kind.value, h.base) for h in hosts] == [(kind, base)]
        stored = db_game_source_handler.get_source_by_path(hosts[0].id, path)
        assert stored is not None

        # The same link again reuses the host instead of creating a twin.
        client.post(
            "/api/catalog/3475/sources",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"url": url.replace("mario", "dr-mario").replace("Mario%2064", "Dr")},
        )
        assert len(db_game_source_handler.get_hosts()) == 1

    def test_add_source_rejects_bad_link(
        self, client, access_token: str, catalog_games
    ):
        for payload in (
            {"url": "ftp://x/y.zip"},
            {"url": "https://archive.org/download/only-item"},
            {},
        ):
            response = client.post(
                "/api/catalog/1074/sources",
                headers={"Authorization": f"Bearer {access_token}"},
                json=payload,
            )
            assert response.status_code in (
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ), payload

    def test_add_source_requires_write_scope(
        self, client, viewer_access_token: str, catalog_games, ia_host: GameHost
    ):
        response = client.post(
            "/api/catalog/1074/sources",
            headers={"Authorization": f"Bearer {viewer_access_token}"},
            json={"host_id": ia_host.id, "path": "x.z64", "platform_slug": "n64"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_game_not_found(self, client, access_token: str, catalog_games):
        response = client.get(
            "/api/catalog/999999", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_filters_facets(
        self,
        client,
        access_token: str,
        catalog_games,
        owned_source: GameSource,
    ):
        response = client.get(
            "/api/catalog/filters",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["total_games"] == 3
        assert body["owned_games"] == 1
        assert body["platforms"] == [
            {
                "slug": "n64",
                "name": "Nintendo 64",
                "game_count": 2,
                "owned_count": 1,
            },
            {
                "slug": "psx",
                "name": "PlayStation",
                "game_count": 1,
                "owned_count": 0,
            },
        ]
        assert body["genres"] == [
            {"name": "Music", "game_count": 1},
            {"name": "Platform", "game_count": 1},
            {"name": "Puzzle", "game_count": 1},
        ]

    def test_upsert_replaces_platforms_and_genres(
        self, client, access_token: str, catalog_games
    ):
        db_catalog_handler.upsert_games(
            [_game(3475, "Dr. Mario 64 (renamed)", platform_slugs=["n64", "psx"])]
        )
        response = client.get(
            "/api/catalog/3475", headers={"Authorization": f"Bearer {access_token}"}
        )
        body = response.json()
        assert body["name"] == "Dr. Mario 64 (renamed)"
        assert body["platform_slugs"] == ["n64", "psx"]
        assert body["genres"] == ["Platform"]
        assert (
            client.get(
                "/api/catalog", headers={"Authorization": f"Bearer {access_token}"}
            ).json()["total"]
            == 3
        )


class TestPlayAndAssets:
    def test_play_sessions_feed_continue_playing(
        self, client, access_token: str, catalog_games
    ):
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post(
            "/api/play/sessions", headers=headers, json={"igdb_id": 3475}
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        play = response.json()
        assert play["igdb_id"] == 3475
        assert play["ended_at"] is None

        response = client.post(
            f"/api/play/sessions/{play['id']}/heartbeat", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        response = client.post(f"/api/play/sessions/{play['id']}/stop", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["ended_at"] is not None

        game = client.get("/api/catalog/3475", headers=headers).json()
        assert game["last_played_at"] is not None
        assert game["play_time_seconds"] >= 0
        other = client.get("/api/catalog/1074", headers=headers).json()
        assert other["last_played_at"] is None

        recent = client.get(
            "/api/catalog?played=true&order_by=last_played&order_dir=desc",
            headers=headers,
        ).json()
        assert [g["name"] for g in recent["items"]] == ["Dr. Mario 64"]

    def test_play_session_unknown_game(self, client, access_token: str, catalog_games):
        response = client.post(
            "/api/play/sessions",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"igdb_id": 999999},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_play_sessions_are_private(
        self, client, access_token: str, viewer_access_token: str, catalog_games
    ):
        play = client.post(
            "/api/play/sessions",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"igdb_id": 3475},
        ).json()
        response = client.post(
            f"/api/play/sessions/{play['id']}/stop",
            headers={"Authorization": f"Bearer {viewer_access_token}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        recent = client.get(
            "/api/catalog?played=true",
            headers={"Authorization": f"Bearer {viewer_access_token}"},
        ).json()
        assert recent["total"] == 0

    def test_saves_round_trip(self, client, access_token: str, catalog_games):
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post(
            "/api/catalog/3475/assets",
            headers=headers,
            data={"kind": "save", "emulator": "mupen64plus_next"},
            files={
                "file": ("Dr. Mario 64.srm", b"SAVEDATA", "application/octet-stream"),
                "screenshot": ("shot.png", b"\x89PNG", "image/png"),
            },
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        asset = response.json()
        assert asset["kind"] == "save"
        assert asset["file_name"] == "Dr. Mario 64.srm"
        assert asset["size"] == 8
        assert asset["has_screenshot"] is True

        listed = client.get(
            "/api/catalog/3475/assets?kind=save&emulator=mupen64plus_next",
            headers=headers,
        ).json()
        assert [a["id"] for a in listed] == [asset["id"]]

        content = client.get(f"/api/assets/{asset['id']}/content", headers=headers)
        assert content.status_code == status.HTTP_200_OK
        assert content.content == b"SAVEDATA"
        shot = client.get(f"/api/assets/{asset['id']}/screenshot", headers=headers)
        assert shot.headers["content-type"] == "image/png"

        # Same core + name overwrites instead of piling up.
        response = client.post(
            "/api/catalog/3475/assets",
            headers=headers,
            data={"kind": "save", "emulator": "mupen64plus_next"},
            files={"file": ("Dr. Mario 64.srm", b"NEWER", "application/octet-stream")},
        )
        assert response.json()["id"] == asset["id"]
        assert response.json()["size"] == 5
        assert (
            client.get(f"/api/assets/{asset['id']}/content", headers=headers).content
            == b"NEWER"
        )

        response = client.delete(f"/api/assets/{asset['id']}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert client.get("/api/catalog/3475/assets", headers=headers).json() == []

    def test_assets_are_private(
        self, client, access_token: str, viewer_access_token: str, catalog_games
    ):
        asset = client.post(
            "/api/catalog/3475/assets",
            headers={"Authorization": f"Bearer {access_token}"},
            data={"kind": "state"},
            files={"file": ("slot1.state", b"STATE", "application/octet-stream")},
        ).json()
        viewer = {"Authorization": f"Bearer {viewer_access_token}"}
        assert client.get("/api/catalog/3475/assets", headers=viewer).json() == []
        assert (
            client.get(f"/api/assets/{asset['id']}/content", headers=viewer).status_code
            == status.HTTP_404_NOT_FOUND
        )
