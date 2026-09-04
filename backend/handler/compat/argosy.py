"""Shapes the catalog into the classic RomM library API that Argosy speaks.

A "rom" here is one catalog game on one platform. Its id packs both, so a
client that only knows rom ids can be answered without any extra table.
"""

from datetime import datetime, timezone
from typing import Any, Final

from handler.metadata.platforms import IGDB_PLATFORM_LIST
from handler.metadata.platforms import UniversalPlatformSlug as UPS
from models.catalog import CatalogGame
from models.game_source import GameSource

# IGDB platform ids stay below this, so rom_id // ROM_ID_BASE is the game.
ROM_ID_BASE: Final = 100_000

PLATFORM_ID_BY_SLUG: Final[dict[str, int]] = {
    slug.value: platform["id"]
    for slug, platform in IGDB_PLATFORM_LIST.items()
    if platform.get("id")
}
SLUG_BY_PLATFORM_ID: Final[dict[int, str]] = {
    platform_id: slug for slug, platform_id in PLATFORM_ID_BY_SLUG.items()
}


def platform_id(slug: str) -> int | None:
    return PLATFORM_ID_BY_SLUG.get(slug)


def platform_slug(platform_id: int) -> str | None:
    return SLUG_BY_PLATFORM_ID.get(platform_id)


def utc_iso(value: datetime | None) -> str | None:
    """A timestamp the way RomM sends one: UTC with a Z, so a client parsing it
    as an instant does not fall back to "now". Column values are naive UTC."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def rom_id(game_id: int, slug: str) -> int | None:
    pid = platform_id(slug)
    return game_id * ROM_ID_BASE + pid if pid is not None else None


def split_rom_id(value: int) -> tuple[int, str | None]:
    """The catalog game id and platform slug a rom id stands for."""
    return value // ROM_ID_BASE, platform_slug(value % ROM_ID_BASE)


def platform_name(slug: str) -> str:
    try:
        return IGDB_PLATFORM_LIST[UPS(slug)]["name"]
    except (ValueError, KeyError):
        return slug


def legacy_platform(slug: str, game_count: int) -> dict[str, Any] | None:
    pid = platform_id(slug)
    if pid is None:
        return None
    name = platform_name(slug)
    return {
        "id": pid,
        "slug": slug,
        "fs_slug": slug,
        "name": name,
        "display_name": name,
        "custom_name": None,
        "rom_count": game_count,
        "url_logo": None,
        "firmware": [],
    }


def _release_ms(game: CatalogGame) -> int | None:
    if game.first_release_date:
        return game.first_release_date * 1000
    if game.release_year:
        return int(
            datetime(game.release_year, 1, 1, tzinfo=timezone.utc).timestamp() * 1000
        )
    return None


def legacy_file(source: GameSource, rid: int) -> dict[str, Any]:
    return {
        "id": source.id,
        "rom_id": rid,
        "file_name": source.filename,
        "file_path": "",
        "file_size_bytes": source.size or 0,
        "full_path": source.filename,
        "category": None,
    }


def legacy_rom(
    game: CatalogGame,
    slug: str,
    sources: list[GameSource],
    *,
    is_favorite: bool = False,
    last_played: datetime | None = None,
) -> dict[str, Any] | None:
    """One platform's view of a catalog game, in the shape of a RomM rom."""
    rid = rom_id(game.id, slug)
    if rid is None:
        return None
    on_platform = [s for s in sources if s.platform_slug == slug]
    primary = on_platform[0] if on_platform else None
    regions = sorted({s.region for s in on_platform if s.region})
    return {
        "id": rid,
        "platform_id": platform_id(slug),
        "platform_slug": slug,
        "platform_display_name": platform_name(slug),
        "name": game.name,
        "slug": game.slug,
        "fs_name": primary.filename if primary else game.name,
        "fs_size_bytes": (primary.size or 0) if primary else 0,
        "full_path": primary.filename if primary else None,
        "igdb_id": game.igdb_id,
        "moby_id": None,
        "summary": game.summary,
        "metadatum": {
            "genres": game.genres,
            "companies": [],
            "first_release_date": _release_ms(game),
            "franchises": [],
            "collections": [],
            "game_modes": [],
            "average_rating": game.rating,
            "player_count": None,
            "age_ratings": [],
        },
        "path_cover_small": None,
        "path_cover_large": None,
        "url_cover": game.url_cover,
        "url_screenshots": game.url_screenshots,
        "regions": regions,
        "languages": [],
        "revision": None,
        "merged_screenshots": [],
        "tags": [],
        "siblings": [],
        "multi": False,
        "has_multiple_files": False,
        "has_simple_single_file": True,
        "has_nested_single_file": False,
        "files": [legacy_file(s, rid) for s in on_platform],
        "youtube_video_id": game.youtube_video_id,
        "alternative_names": [],
        "has_manual": False,
        "is_identified": True,
        "has_download": primary is not None,
        "rom_user": {
            "rating": 0,
            "difficulty": 0,
            "completion": 0,
            "status": None,
            "backlogged": False,
            "now_playing": False,
            "hidden": False,
            "is_favorite": is_favorite,
            "last_played": utc_iso(last_played),
        },
    }
