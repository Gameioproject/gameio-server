"""The classic library API Argosy uses, answered from the catalog."""

import gzip
import hashlib

from fastapi import status
from sqlalchemy import update

from handler.compat.argosy import ROM_ID_BASE, platform_id, rom_id, split_rom_id
from handler.database import (
    db_catalog_handler,
    db_game_activity_handler,
    db_game_source_handler,
)
from handler.database.base_handler import sync_session
from handler.database.catalog_handler import CatalogGameInput
from models.game_activity import GZIP_ENCODING, GameAsset, GameAssetKind
from models.game_source import GameHostKind


def _game(igdb_id: int, name: str, platforms: list[str]) -> CatalogGameInput:
    return {
        "igdb_id": igdb_id,
        "name": name,
        "slug": name.lower().replace(" ", "-"),
        "summary": "A game",
        "release_year": 1996,
        "first_release_date": None,
        "cover_image_id": "co1abc",
        "screenshot_image_ids": ["sc1"],
        "genres": ["Platform"],
        "platform_slugs": platforms,
        "rating": 90.0,
        "rating_count": 10,
        "youtube_video_id": None,
        "igdb_url": None,
        "source_updated_at": None,
    }


def test_rom_id_round_trip():
    n64 = platform_id("n64")
    assert n64 is not None and n64 < ROM_ID_BASE
    rid = rom_id(42, "n64")
    assert rid == 42 * ROM_ID_BASE + n64
    assert split_rom_id(rid) == (42, "n64")
    assert rom_id(1, "not-a-platform") is None


class TestClassicLibrary:
    def _seed(self):
        db_catalog_handler.upsert_games(
            [
                _game(1074, "Super Mario 64", ["n64"]),
                _game(3475, "Dr. Mario 64", ["n64", "ngc"]),
                _game(6080, "PaRappa the Rapper", ["psx"]),
            ]
        )
        host = db_game_source_handler.add_host(
            name="N64",
            kind=GameHostKind.INTERNET_ARCHIVE,
            base="item",
            platform_slug="n64",
        )
        mario = db_catalog_handler.get_game_by_igdb_id(1074)
        assert mario
        db_game_source_handler.upsert_sources(
            host.id,
            [
                {
                    "catalog_game_id": mario["game"].id,
                    "path": "Super Mario 64 (USA).z64",
                    "filename": "Super Mario 64 (USA).z64",
                    "platform_slug": "n64",
                    "size": 8388608,
                    "md5": None,
                    "sha1": None,
                    "region": "USA",
                }
            ],
        )
        return mario["game"].id

    def test_platforms_and_roms(self, client, access_token: str):
        mario_id = self._seed()
        headers = {"Authorization": f"Bearer {access_token}"}

        platforms = client.get("/api/platforms", headers=headers).json()
        by_slug = {p["slug"]: p for p in platforms}
        assert by_slug["n64"]["rom_count"] == 2
        assert by_slug["n64"]["id"] == platform_id("n64")
        assert client.get(
            "/api/platforms/identifiers", headers=headers
        ).json() == sorted(p["id"] for p in platforms)

        page = client.get(
            f"/api/roms?platform_ids={by_slug['n64']['id']}&limit=10&offset=0",
            headers=headers,
        ).json()
        assert page["total"] == 2
        names = [r["name"] for r in page["items"]]
        assert names == ["Dr. Mario 64", "Super Mario 64"]
        mario = next(r for r in page["items"] if r["name"] == "Super Mario 64")
        assert mario["id"] == rom_id(mario_id, "n64")
        assert mario["fs_name"] == "Super Mario 64 (USA).z64"
        assert mario["fs_size_bytes"] == 8388608
        assert mario["files"][0]["file_name"] == "Super Mario 64 (USA).z64"
        assert mario["regions"] == ["USA"]
        assert mario["url_cover"].endswith("/t_1080p/co1abc.jpg")
        assert mario["path_cover_large"].endswith("/t_cover_big_2x/co1abc.jpg")
        assert mario["path_cover_small"].endswith("/t_cover_big/co1abc.jpg")
        assert mario["metadatum"]["genres"] == ["Platform"]
        assert mario["has_download"] is True

        dr = next(r for r in page["items"] if r["name"] == "Dr. Mario 64")
        assert dr["has_download"] is False and dr["files"] == []

        single = client.get(f"/api/roms/{mario['id']}", headers=headers).json()
        assert single["name"] == "Super Mario 64"
        assert client.get("/api/roms/123", headers=headers).status_code == 404

        ids = client.get("/api/roms/identifiers", headers=headers).json()
        assert mario["id"] in ids and rom_id(dr["id"] // ROM_ID_BASE, "ngc") in ids

    def test_download_redirects_to_the_host(self, client, access_token: str):
        mario_id = self._seed()
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get(
            f"/api/roms/{rom_id(mario_id, 'n64')}/content/anything.z64",
            headers=headers,
            follow_redirects=False,
        )
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"].startswith(
            "https://archive.org/download/item/Super%20Mario%2064"
        )
        dr = db_catalog_handler.get_game_by_igdb_id(3475)
        assert dr
        missing = client.get(
            f"/api/roms/{rom_id(dr['game'].id, 'n64')}/content/x", headers=headers
        )
        assert missing.status_code == 404

    def test_favorites_through_rom_props_and_collections(
        self, client, access_token: str
    ):
        mario_id = self._seed()
        headers = {"Authorization": f"Bearer {access_token}"}
        rid = rom_id(mario_id, "n64")
        assert client.put(
            f"/api/roms/{rid}/props", headers=headers, json={"is_favorite": True}
        ).json()["is_favorite"]
        favorites = client.get(
            "/api/collections?is_favorite=true", headers=headers
        ).json()
        assert len(favorites) == 1 and favorites[0]["rom_ids"] == [rid]
        assert (
            client.get("/api/collections?is_favorite=false", headers=headers).json()
            == []
        )

        dr = db_catalog_handler.get_game_by_igdb_id(3475)
        assert dr
        updated = client.put(
            f"/api/collections/{favorites[0]['id']}",
            headers=headers,
            data={"rom_ids": f"[{rom_id(dr['game'].id, 'ngc')}]"},
        ).json()
        assert updated["game_igdb_ids"] == [3475]
        assert rom_id(dr["game"].id, "n64") in updated["rom_ids"]

        assert (
            client.get(
                "/api/collections/virtual?type=collection", headers=headers
            ).json()
            == []
        )
        assert client.get("/api/collections/smart", headers=headers).json() == []

    def test_play_sessions_ingest(self, client, access_token: str):
        mario_id = self._seed()
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post(
            "/api/play-sessions",
            headers=headers,
            json={
                "device_id": "handheld",
                "sessions": [
                    {
                        "rom_id": rom_id(mario_id, "n64"),
                        "start_time": "2026-08-29T10:00:00Z",
                        "end_time": "2026-08-29T10:30:00Z",
                        "duration_ms": 1800000,
                    },
                    {
                        "rom_id": 999 * ROM_ID_BASE,
                        "start_time": "2026-08-29T10:00:00Z",
                        "end_time": "2026-08-29T10:01:00Z",
                        "duration_ms": 60000,
                    },
                ],
            },
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["created_count"] == 1 and body["skipped_count"] == 1
        played = client.get("/api/catalog?played=true", headers=headers).json()
        assert [g["name"] for g in played["items"]] == ["Super Mario 64"]
        assert played["items"][0]["play_time_seconds"] == 1800
        assert (
            client.post("/api/activity/heartbeat", headers=headers).status_code == 200
        )
        assert client.get("/api/saves", headers=headers).json() == []

    def test_states_are_stored_gzipped_and_served_raw_or_gzipped(
        self, client, access_token: str
    ):
        mario_id = self._seed()
        rid = rom_id(mario_id, "n64")
        headers = {"Authorization": f"Bearer {access_token}"}
        raw = b"\x00" * 4096 + b"STATE"
        sent = gzip.compress(raw)
        response = client.post(
            f"/api/states?rom_id={rid}&emulator=mupen64plus_next&channel=autosave&slot=-1",
            headers=headers,
            files={"stateFile": ("mario.state", sent, "application/gzip")},
        )
        assert response.status_code == 200, response.text
        state = response.json()
        assert state["file_size_bytes"] == len(raw)
        assert state["content_hash"] == hashlib.sha256(raw).hexdigest()

        stored = db_game_activity_handler.get_asset(state["id"])
        assert stored.content_encoding == GZIP_ENCODING
        assert stored.content == sent

        url = f"/api/states/{state['id']}/content"
        plain = client.get(url, headers={**headers, "Accept-Encoding": "identity"})
        assert plain.headers.get("content-encoding") is None
        assert plain.content == raw
        zipped = client.get(url, headers={**headers, "Accept-Encoding": "gzip"})
        assert zipped.headers["content-encoding"] == "gzip"
        assert zipped.content == raw
        assert (
            client.get(f"/api/assets/{state['id']}/content", headers=headers).content
            == raw
        )

    def test_saves_sent_raw_are_compressed_and_legacy_raw_rows_still_serve(
        self, client, access_token: str
    ):
        mario_id = self._seed()
        rid = rom_id(mario_id, "n64")
        headers = {"Authorization": f"Bearer {access_token}"}
        raw = b"\xff" * 2048
        save = client.post(
            f"/api/saves?rom_id={rid}&emulator=mupen64plus_next",
            headers=headers,
            files={"saveFile": ("mario.eep", raw, "application/octet-stream")},
        ).json()
        assert (
            db_game_activity_handler.get_asset(save["id"]).content_encoding
            == GZIP_ENCODING
        )

        tiny = client.post(
            f"/api/saves?rom_id={rid}&emulator=mupen64plus_next&channel=tiny",
            headers=headers,
            files={"saveFile": ("tiny.eep", b"AB", "application/octet-stream")},
        ).json()
        assert db_game_activity_handler.get_asset(tiny["id"]).content_encoding is None

        legacy = db_game_activity_handler.upsert_asset(
            user_id=db_game_activity_handler.get_asset(save["id"]).user_id,
            catalog_game_id=mario_id,
            kind=GameAssetKind.STATE,
            emulator="mupen64plus_next",
            file_name="legacy.state",
            content=raw,
            screenshot=None,
        )
        with sync_session.begin() as session:
            session.execute(
                update(GameAsset)
                .where(GameAsset.id == legacy.id)
                .values(content=raw, content_encoding=None)
            )
        for encoding in ("identity", "gzip"):
            for asset_id, kind, body in (
                (save["id"], "saves", raw),
                (tiny["id"], "saves", b"AB"),
                (legacy.id, "states", raw),
            ):
                response = client.get(
                    f"/api/{kind}/{asset_id}/content",
                    headers={**headers, "Accept-Encoding": encoding},
                )
                assert response.content == body

    def test_heartbeat_marks_catalog_only(self, client):
        system = client.get("/api/heartbeat").json()["SYSTEM"]
        assert system["CATALOG_ONLY"] is True
        assert system["VERSION"].split("-")[0].count(".") == 2
