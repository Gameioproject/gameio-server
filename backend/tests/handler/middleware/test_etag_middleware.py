from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from handler.middleware.etag_middleware import ETagMiddleware


def create_test_app() -> Starlette:
    async def roms(_):
        return JSONResponse({"items": [1, 2, 3]})

    async def text(_):
        return PlainTextResponse("hello")

    async def cached(_):
        return JSONResponse({"a": 1}, headers={"cache-control": "no-store"})

    async def missing(_):
        return JSONResponse({"detail": "nope"}, status_code=404)

    async def outside(_):
        return JSONResponse({"a": 1})

    return Starlette(
        routes=[
            Route("/api/roms", roms, methods=["GET", "POST"]),
            Route("/api/text", text),
            Route("/api/cached", cached),
            Route("/api/missing", missing),
            Route("/outside", outside),
        ],
        middleware=[Middleware(ETagMiddleware)],
    )


class TestETagMiddleware:
    def test_tags_json_and_revalidates(self):
        client = TestClient(create_test_app())
        first = client.get("/api/roms")
        etag = first.headers["etag"]

        assert first.status_code == 200
        assert etag.startswith('W/"')
        assert first.headers["cache-control"] == "private, no-cache"

        second = client.get("/api/roms", headers={"If-None-Match": etag})
        assert second.status_code == 304
        assert second.content == b""
        assert second.headers["etag"] == etag

    def test_matches_strong_and_listed_validators(self):
        client = TestClient(create_test_app())
        opaque = client.get("/api/roms").headers["etag"].removeprefix("W/")

        response = client.get("/api/roms", headers={"If-None-Match": f'"x", {opaque}'})
        assert response.status_code == 304

    def test_changed_body_returns_full_response(self):
        client = TestClient(create_test_app())
        response = client.get("/api/roms", headers={"If-None-Match": 'W/"stale"'})

        assert response.status_code == 200
        assert response.json() == {"items": [1, 2, 3]}

    def test_skips_non_json_errors_preset_headers_and_other_paths(self):
        client = TestClient(create_test_app())

        assert "etag" not in client.get("/api/text").headers
        assert "etag" not in client.get("/api/missing").headers
        assert client.get("/api/cached").headers["cache-control"] == "no-store"
        assert "etag" not in client.get("/api/cached").headers
        assert "etag" not in client.get("/outside").headers

    def test_skips_non_get(self):
        client = TestClient(create_test_app())
        assert "etag" not in client.post("/api/roms").headers
