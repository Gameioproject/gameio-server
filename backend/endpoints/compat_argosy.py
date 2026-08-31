"""The classic RomM library API, answered from the catalog for Argosy."""

from datetime import datetime
from typing import Annotated, Any

from fastapi import HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from decorators.auth import protected_route
from handler.auth.constants import Scope
from handler.compat import argosy
from handler.database import (
    db_catalog_handler,
    db_collection_handler,
    db_game_activity_handler,
)
from handler.database.catalog_handler import CatalogOrderBy, CatalogOrderDir
from utils.router import APIRouter

router = APIRouter(tags=["argosy compatibility"])

ROMS_PAGE_MAX_LIMIT = 500


def _platform_or_404(platform_id: int) -> str:
    slug = argosy.platform_slug(platform_id)
    if slug is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Platform {platform_id} not found",
        )
    return slug


def _platforms() -> list[dict[str, Any]]:
    platforms = []
    for row in db_catalog_handler.get_platform_counts():
        platform = argosy.legacy_platform(row["value"], row["game_count"])
        if platform is not None:
            platforms.append(platform)
    return sorted(platforms, key=lambda p: p["name"])


@protected_route(router.get, "/platforms", [Scope.ROMS_READ])
def get_platforms(request: Request) -> list[dict[str, Any]]:
    return _platforms()


@protected_route(router.get, "/platforms/identifiers", [Scope.ROMS_READ])
def get_platform_identifiers(request: Request) -> list[int]:
    return sorted(p["id"] for p in _platforms())


@protected_route(router.get, "/platforms/{platform_id}", [Scope.ROMS_READ])
def get_platform(request: Request, platform_id: int) -> dict[str, Any]:
    slug = _platform_or_404(platform_id)
    counts = {
        r["value"]: r["game_count"] for r in db_catalog_handler.get_platform_counts()
    }
    platform = argosy.legacy_platform(slug, counts.get(slug, 0))
    assert platform is not None
    return platform


def _roms_for(request: Request, matches, slug: str) -> list[dict[str, Any]]:
    favorites = db_collection_handler.get_favorite_igdb_ids(request.user.id)
    stats = db_game_activity_handler.get_play_stats(
        request.user.id, [m["game"].id for m in matches]
    )
    roms = []
    for match in matches:
        game = match["game"]
        played = stats.get(game.id)
        rom = argosy.legacy_rom(
            game,
            slug,
            match["sources"],
            is_favorite=game.igdb_id in favorites,
            last_played=played["last_played_at"] if played else None,
        )
        if rom is not None:
            roms.append(rom)
    return roms


def _roms_any_platform(request: Request, matches) -> list[dict[str, Any]]:
    """Search results span platforms, so each game is returned under its own first one."""
    by_slug: dict[str, list[Any]] = {}
    for match in matches:
        slugs = [p.platform_slug for p in match["game"].platforms]
        if not slugs:
            continue
        by_slug.setdefault(sorted(slugs)[0], []).append(match)
    roms: list[dict[str, Any]] = []
    for slug, group in by_slug.items():
        roms.extend(_roms_for(request, group, slug))
    return roms


@protected_route(router.get, "/roms", [Scope.ROMS_READ])
def get_roms(
    request: Request,
    platform_ids: Annotated[str | None, Query()] = None,
    search_term: Annotated[str | None, Query()] = None,
    owned: Annotated[bool | None, Query()] = None,
    order_by: Annotated[str, Query()] = "id",
    order_dir: Annotated[str, Query()] = "asc",
    limit: Annotated[int, Query(ge=1, le=ROMS_PAGE_MAX_LIMIT)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    """One page of a platform's games, or of the whole catalog when searching without one."""
    first = (platform_ids or "").split(",")[0].strip()
    # A search may span the server, so a platform is only required when browsing.
    if not first.isdigit():
        if not search_term:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="platform_ids is required unless search_term is given",
            )
        slug = None
    else:
        slug = _platform_or_404(int(first))
    matches, total = db_catalog_handler.get_games(
        search=search_term,
        owned=owned,
        platform_slug=slug,
        order_by=CatalogOrderBy.NAME,
        order_dir=CatalogOrderDir.DESC if order_dir == "desc" else CatalogOrderDir.ASC,
        limit=limit,
        offset=offset,
    )
    return {
        "items": _roms_for(request, matches, slug) if slug else _roms_any_platform(request, matches),
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@protected_route(router.get, "/roms/sections", [Scope.ROMS_READ])
def get_rom_sections(
    request: Request,
    platform_ids: Annotated[str | None, Query()] = None,
) -> list[dict[str, Any]]:
    """The A-Z index for a platform: where each initial starts in name order, and how many.

    Lets a client show the whole alphabet and jump into it without having paged that far.
    """
    first = (platform_ids or "").split(",")[0].strip()
    slug = _platform_or_404(int(first)) if first.isdigit() else None
    return db_catalog_handler.get_name_sections(platform_slug=slug)


@protected_route(router.get, "/roms/identifiers", [Scope.ROMS_READ])
def get_rom_identifiers(request: Request) -> list[int]:
    ids = (
        argosy.rom_id(game_id, slug)
        for game_id, slug in db_catalog_handler.get_platform_pairs()
    )
    return sorted(i for i in ids if i is not None)


def _rom_or_404(request: Request, rom_id: int) -> dict[str, Any]:
    game_id, slug = argosy.split_rom_id(rom_id)
    match = db_catalog_handler.get_game(game_id) if slug else None
    if match is None or slug is None or slug not in match["game"].platform_slugs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rom {rom_id} not found"
        )
    return _roms_for(request, [match], slug)[0]


@protected_route(router.get, "/roms/{rom_id}", [Scope.ROMS_READ])
def get_rom(request: Request, rom_id: int) -> dict[str, Any]:
    return _rom_or_404(request, rom_id)


def _download_target(rom_id: int) -> str:
    game_id, slug = argosy.split_rom_id(rom_id)
    match = db_catalog_handler.get_game(game_id) if slug else None
    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rom {rom_id} not found"
        )
    sources = [s for s in match["sources"] if s.platform_slug == slug]
    if not sources:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{match['game'].name} has no download link on {slug}",
        )
    return sources[0].url


@protected_route(router.get, "/roms/{rom_id}/content/{file_name}", [Scope.ROMS_READ])
@protected_route(router.head, "/roms/{rom_id}/content/{file_name}", [Scope.ROMS_READ])
def download_rom(request: Request, rom_id: int, file_name: str) -> RedirectResponse:
    """Argosy downloads through the classic route; the file lives on the game's host."""
    return RedirectResponse(_download_target(rom_id), status_code=status.HTTP_302_FOUND)


class RomPropsUpdate(BaseModel):
    is_favorite: bool | None = None


@protected_route(router.put, "/roms/{rom_id}/props", [Scope.ROMS_USER_WRITE])
def update_rom_props(
    request: Request, rom_id: int, body: RomPropsUpdate
) -> dict[str, Any]:
    """Only the favorite flag has a home here; ratings and statuses are not kept."""
    rom = _rom_or_404(request, rom_id)
    if body.is_favorite is not None:
        favorites = db_collection_handler.get_or_create_favorite_collection(
            request.user.id
        )
        if body.is_favorite:
            db_collection_handler.add_games_to_collection(
                favorites.id, [rom["igdb_id"]]
            )
        else:
            db_collection_handler.remove_games_from_collection(
                favorites.id, [rom["igdb_id"]]
            )
        rom["rom_user"]["is_favorite"] = body.is_favorite
    return rom["rom_user"]


@protected_route(router.get, "/collections/virtual", [Scope.COLLECTIONS_READ])
def get_virtual_collections(request: Request) -> list[Any]:
    return []


@protected_route(router.get, "/collections/smart", [Scope.COLLECTIONS_READ])
def get_smart_collections(request: Request) -> list[Any]:
    return []


@protected_route(router.get, "/saves", [Scope.ASSETS_READ])
def get_saves(request: Request) -> list[Any]:
    """Saves live per catalog game under /api/catalog; the classic list is always empty."""
    return []


@protected_route(router.get, "/states", [Scope.ASSETS_READ])
def get_states(request: Request) -> list[Any]:
    return []


class PlaySessionEntry(BaseModel):
    rom_id: int | None = None
    start_time: datetime
    end_time: datetime
    duration_ms: int = 0


class PlaySessionIngest(BaseModel):
    device_id: str | None = None
    sessions: list[PlaySessionEntry] = []


@protected_route(router.post, "/play-sessions", [Scope.ROMS_USER_WRITE])
def ingest_play_sessions(request: Request, body: PlaySessionIngest) -> dict[str, Any]:
    """Sittings Argosy recorded offline become the same sessions the web player writes."""
    results = []
    created = 0
    for index, entry in enumerate(body.sessions):
        game_id, slug = argosy.split_rom_id(entry.rom_id or 0)
        if not slug or db_catalog_handler.get_game(game_id) is None:
            results.append(
                {"index": index, "status": "skipped", "detail": "unknown rom"}
            )
            continue
        play = db_game_activity_handler.record_session(
            user_id=request.user.id,
            catalog_game_id=game_id,
            device_id=body.device_id,
            started_at=entry.start_time,
            ended_at=entry.end_time,
            duration_seconds=max(0, entry.duration_ms // 1000),
        )
        created += 1
        results.append({"index": index, "status": "created", "id": play.id})
    return {
        "results": results,
        "created_count": created,
        "skipped_count": len(body.sessions) - created,
    }


@protected_route(router.post, "/activity/heartbeat", [Scope.ROMS_USER_WRITE])
@protected_route(router.delete, "/activity/heartbeat", [Scope.ROMS_USER_WRITE])
def activity_heartbeat(request: Request) -> dict[str, Any]:
    """Presence is not tracked; answering keeps the client's session loop quiet."""
    return {}
