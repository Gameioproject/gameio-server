from collections.abc import AsyncIterator
from typing import Annotated, Final

import httpx
from fastapi import HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse, StreamingResponse

from decorators.auth import protected_route
from endpoints.responses.catalog import (
    CatalogFiltersSchema,
    CatalogGameSchema,
    CatalogGenreSchema,
    CatalogPageSchema,
    CatalogPlatformSchema,
)
from endpoints.responses.game_source import GameSourceCreateSchema, GameSourceSchema
from handler.auth.constants import Scope
from handler.database import (
    db_catalog_handler,
    db_collection_handler,
    db_game_activity_handler,
    db_game_source_handler,
)
from handler.database.catalog_handler import CatalogOrderBy, CatalogOrderDir
from handler.metadata.platforms import IGDB_PLATFORM_LIST
from handler.metadata.platforms import UniversalPlatformSlug as UPS
from handler.sources.locator import find_or_create_host, parse_direct_link
from models.game_source import GameSource
from utils.context import ctx_httpx_client
from utils.router import APIRouter

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"],
)

CATALOG_PAGE_MAX_LIMIT = 500
STREAM_CHUNK_SIZE: Final = 1024 * 1024
STREAM_TIMEOUT: Final = httpx.Timeout(30.0, read=120.0)
# Upstream headers the browser needs to size and resume the transfer.
STREAM_PASSTHROUGH_HEADERS: Final = (
    "content-length",
    "content-range",
    "accept-ranges",
    "last-modified",
    "etag",
)


def _platform_name(slug: str) -> str:
    try:
        return IGDB_PLATFORM_LIST[UPS(slug)]["name"]
    except (ValueError, KeyError):
        return slug


def _favorite_ids(request: Request) -> set[int]:
    return db_collection_handler.get_favorite_igdb_ids(request.user.id)


def _play_stats(request: Request, matches):
    return db_game_activity_handler.get_play_stats(
        request.user.id, [m["game"].id for m in matches]
    )


def _get_match(igdb_id: int):
    match = db_catalog_handler.get_game_by_igdb_id(igdb_id)
    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog game with IGDB id {igdb_id} not found",
        )
    return match


@protected_route(router.get, "", [Scope.ROMS_READ])
def get_catalog_games(
    request: Request,
    search: Annotated[
        str | None, Query(description="Words to match in the name")
    ] = None,
    platform_slug: Annotated[str | None, Query()] = None,
    exclude_platform: Annotated[
        list[str] | None, Query(description="Platforms the user chose to hide")
    ] = None,
    genre: Annotated[str | None, Query()] = None,
    min_rating: Annotated[float | None, Query(ge=0, le=100)] = None,
    year_from: Annotated[int | None, Query()] = None,
    year_to: Annotated[int | None, Query()] = None,
    owned: Annotated[
        bool | None,
        Query(
            description="Only games with (true) or without (false) a download source"
        ),
    ] = None,
    owned_platforms: Annotated[
        bool | None,
        Query(description="Only games on platforms that have a download source"),
    ] = None,
    collection_id: Annotated[
        int | None, Query(description="Only games in this collection")
    ] = None,
    favorite: Annotated[
        bool | None, Query(description="Only the user's favorite games")
    ] = None,
    played: Annotated[
        bool | None, Query(description="Only games the user has played")
    ] = None,
    order_by: Annotated[CatalogOrderBy, Query()] = CatalogOrderBy.RATING,
    order_dir: Annotated[CatalogOrderDir, Query()] = CatalogOrderDir.DESC,
    limit: Annotated[int, Query(ge=1, le=CATALOG_PAGE_MAX_LIMIT)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CatalogPageSchema:
    """Browse the metadata catalog, with each game's download sources."""
    favorite_ids = _favorite_ids(request)
    if favorite:
        favorites = db_collection_handler.get_favorite_collection(request.user.id)
        if favorites is None:
            return CatalogPageSchema(items=[], total=0, limit=limit, offset=offset)
        collection_id = favorites.id
    matches, total = db_catalog_handler.get_games(
        search=search,
        platform_slug=platform_slug,
        exclude_platform_slugs=exclude_platform,
        genre=genre,
        min_rating=min_rating,
        year_from=year_from,
        year_to=year_to,
        owned=owned,
        owned_platforms=owned_platforms,
        collection_id=collection_id,
        played_by=(
            request.user.id
            if (played or order_by == CatalogOrderBy.LAST_PLAYED)
            else None
        ),
        order_by=order_by,
        order_dir=order_dir,
        limit=limit,
        offset=offset,
    )
    play_stats = _play_stats(request, matches)
    return CatalogPageSchema(
        items=[
            CatalogGameSchema.from_match(m, favorite_ids, play_stats) for m in matches
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@protected_route(router.get, "/filters", [Scope.ROMS_READ])
def get_catalog_filters(request: Request) -> CatalogFiltersSchema:
    """Facets for the catalog browser: platforms and genres with counts, plus totals."""
    total_games, owned_games = db_catalog_handler.get_totals()
    return CatalogFiltersSchema(
        total_games=total_games,
        owned_games=owned_games,
        platforms=[
            CatalogPlatformSchema(
                slug=facet["value"],
                name=_platform_name(facet["value"]),
                game_count=facet["game_count"],
                owned_count=facet["owned_count"],
            )
            for facet in db_catalog_handler.get_platform_counts()
        ],
        genres=[
            CatalogGenreSchema(name=facet["value"], game_count=facet["game_count"])
            for facet in db_catalog_handler.get_genre_counts()
        ],
    )


@protected_route(
    router.get,
    "/{igdb_id}",
    [Scope.ROMS_READ],
    responses={status.HTTP_404_NOT_FOUND: {}},
)
def get_catalog_game(request: Request, igdb_id: int) -> CatalogGameSchema:
    match = _get_match(igdb_id)
    return CatalogGameSchema.from_match(
        match, _favorite_ids(request), _play_stats(request, [match])
    )


@protected_route(
    router.get,
    "/{igdb_id}/download",
    [Scope.ROMS_READ],
    responses={
        status.HTTP_302_FOUND: {},
        status.HTTP_404_NOT_FOUND: {},
    },
)
def download_catalog_game(
    request: Request,
    igdb_id: int,
    source_id: Annotated[
        int | None, Query(description="Pick one source instead of the first")
    ] = None,
) -> RedirectResponse:
    """Redirect to the game's file on its host; the server never serves the bytes."""
    source = _pick_source(igdb_id, source_id)
    headers = {"X-Source-Filename": source.filename}
    if source.size is not None:
        headers["X-Source-Size"] = str(source.size)
    if source.md5:
        headers["X-Source-MD5"] = source.md5
    if source.sha1:
        headers["X-Source-SHA1"] = source.sha1
    return RedirectResponse(
        url=source.url, status_code=status.HTTP_302_FOUND, headers=headers
    )


def _pick_source(igdb_id: int, source_id: int | None) -> GameSource:
    sources = _get_match(igdb_id)["sources"]
    if source_id is not None:
        sources = [s for s in sources if s.id == source_id]
    if not sources:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No download source for IGDB id {igdb_id}",
        )
    return sources[0]


async def _stream_source(
    request: Request, source: GameSource, *, head_only: bool
) -> StreamingResponse:
    """Pipe the file from its host to the client without storing it."""
    client = ctx_httpx_client.get()
    upstream_headers = {}
    if range_header := request.headers.get("range"):
        upstream_headers["Range"] = range_header
    upstream = client.stream(
        "HEAD" if head_only else "GET",
        source.url,
        headers=upstream_headers,
        follow_redirects=True,
        timeout=STREAM_TIMEOUT,
    )
    response = await upstream.__aenter__()
    if response.status_code >= 400:
        await upstream.__aexit__(None, None, None)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Host answered {response.status_code} for {source.filename}",
        )

    headers = {
        key: response.headers[key]
        for key in STREAM_PASSTHROUGH_HEADERS
        if key in response.headers
    }
    headers["Content-Disposition"] = f'attachment; filename="{source.filename}"'

    async def body() -> AsyncIterator[bytes]:
        try:
            if not head_only:
                async for chunk in response.aiter_bytes(STREAM_CHUNK_SIZE):
                    yield chunk
        finally:
            await upstream.__aexit__(None, None, None)

    return StreamingResponse(
        body(),
        status_code=response.status_code,
        media_type="application/octet-stream",
        headers=headers,
    )


@protected_route(
    router.get,
    "/{igdb_id}/stream",
    [Scope.ROMS_READ],
    responses={
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_502_BAD_GATEWAY: {},
    },
)
async def stream_catalog_game(
    request: Request,
    igdb_id: int,
    source_id: Annotated[int | None, Query()] = None,
) -> StreamingResponse:
    """Relay the file for the browser player: hosts rarely send CORS headers,
    so a cross-origin fetch of the redirect target is blocked. Nothing is stored."""
    source = _pick_source(igdb_id, source_id)
    return await _stream_source(request, source, head_only=False)


@protected_route(
    router.head,
    "/{igdb_id}/stream",
    [Scope.ROMS_READ],
    responses={
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_502_BAD_GATEWAY: {},
    },
)
async def head_catalog_game_stream(
    request: Request,
    igdb_id: int,
    source_id: Annotated[int | None, Query()] = None,
) -> StreamingResponse:
    source = _pick_source(igdb_id, source_id)
    return await _stream_source(request, source, head_only=True)


@protected_route(
    router.head,
    "/{igdb_id}/download",
    [Scope.ROMS_READ],
    responses={
        status.HTTP_302_FOUND: {},
        status.HTTP_404_NOT_FOUND: {},
    },
)
def head_catalog_game_download(
    request: Request,
    igdb_id: int,
    source_id: Annotated[int | None, Query()] = None,
) -> RedirectResponse:
    """EmulatorJS probes the game URL with HEAD before fetching it."""
    return download_catalog_game(request, igdb_id, source_id)


@protected_route(
    router.post,
    "/{igdb_id}/sources",
    [Scope.ROMS_WRITE],
    responses={status.HTTP_404_NOT_FOUND: {}},
)
def add_catalog_game_source(
    request: Request, igdb_id: int, body: GameSourceCreateSchema
) -> GameSourceSchema:
    """Attach a file on a host to a catalog game by hand, by host + path or by direct link."""
    match = _get_match(igdb_id)
    game = match["game"]
    platform_slug = body.platform_slug or next(iter(game.platform_slugs), None)
    if not platform_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The game has no platform; pass platform_slug",
        )

    if body.url:
        try:
            locator = parse_direct_link(body.url)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc
        host_id = find_or_create_host(locator, platform_slug).id
        path = locator.path
    else:
        assert body.host_id is not None and body.path is not None
        if db_game_source_handler.get_host(body.host_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game host {body.host_id} not found",
            )
        host_id, path = body.host_id, body.path

    db_game_source_handler.upsert_sources(
        host_id,
        [
            {
                "catalog_game_id": game.id,
                "path": path,
                "filename": body.filename or path.rsplit("/", 1)[-1],
                "platform_slug": platform_slug,
                "size": body.size,
                "md5": body.md5,
                "sha1": body.sha1,
                "region": body.region,
            }
        ],
    )
    source = db_game_source_handler.get_source_by_path(host_id, path)
    assert source is not None
    return GameSourceSchema.from_source(source)


@protected_route(
    router.delete,
    "/sources/{source_id}",
    [Scope.ROMS_WRITE],
    responses={status.HTTP_404_NOT_FOUND: {}},
)
def delete_catalog_game_source(request: Request, source_id: int) -> None:
    if not db_game_source_handler.delete_source(source_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found",
        )
