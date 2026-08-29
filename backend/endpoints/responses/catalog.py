from collections.abc import Mapping
from collections.abc import Set as AbstractSet

from pydantic import ConfigDict

from handler.database.catalog_handler import CatalogGameMatch
from handler.database.game_activity_handler import PlayStats
from models.catalog import CatalogGame

from .base import BaseModel, UTCDatetime
from .game_source import GameSourceSchema


class CatalogGameSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    igdb_id: int
    name: str
    slug: str | None
    summary: str | None
    release_year: int | None
    first_release_date: int | None
    url_cover: str | None
    url_cover_small: str | None
    url_screenshots: list[str]
    genres: list[str]
    platform_slugs: list[str]
    rating: float | None
    rating_count: int
    youtube_video_id: str | None
    igdb_url: str | None

    # Owned means at least one download source exists on an enabled host.
    owned: bool
    sources: list[GameSourceSchema]
    # In the requesting user's favorites collection.
    is_favorite: bool
    # The requesting user's play history, from sessions reported by any client.
    last_played_at: UTCDatetime | None
    play_time_seconds: int

    @classmethod
    def from_match(
        cls,
        match: CatalogGameMatch,
        favorite_igdb_ids: AbstractSet[int] = frozenset(),
        play_stats: Mapping[int, PlayStats] | None = None,
    ) -> "CatalogGameSchema":
        game: CatalogGame = match["game"]
        sources = match["sources"]
        stats = (play_stats or {}).get(game.id)
        return cls(
            id=game.id,
            igdb_id=game.igdb_id,
            name=game.name,
            slug=game.slug,
            summary=game.summary,
            release_year=game.release_year,
            first_release_date=game.first_release_date,
            url_cover=game.url_cover,
            url_cover_small=game.url_cover_small,
            url_screenshots=game.url_screenshots,
            genres=game.genres,
            platform_slugs=game.platform_slugs,
            rating=game.rating,
            rating_count=game.rating_count,
            youtube_video_id=game.youtube_video_id,
            igdb_url=game.igdb_url,
            owned=bool(sources),
            sources=[GameSourceSchema.from_source(s) for s in sources],
            is_favorite=game.igdb_id in favorite_igdb_ids,
            last_played_at=stats["last_played_at"] if stats else None,  # type: ignore[arg-type]
            play_time_seconds=stats["play_time_seconds"] if stats else 0,
        )


class CatalogPageSchema(BaseModel):
    items: list[CatalogGameSchema]
    total: int
    limit: int
    offset: int


class CatalogPlatformSchema(BaseModel):
    slug: str
    name: str
    game_count: int
    owned_count: int


class CatalogGenreSchema(BaseModel):
    name: str
    game_count: int


class CatalogFiltersSchema(BaseModel):
    total_games: int
    owned_games: int
    platforms: list[CatalogPlatformSchema]
    genres: list[CatalogGenreSchema]
