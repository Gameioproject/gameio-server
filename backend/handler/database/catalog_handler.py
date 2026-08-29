import enum
from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypedDict

from sqlalchemy import Select, case, func, select
from sqlalchemy.orm import Session

from decorators.database import begin_session
from models.catalog import CatalogGame, CatalogGameGenre, CatalogGamePlatform
from models.collection import CollectionGame
from models.game_activity import GamePlaySession
from models.game_source import GameHost, GameSource

from .base_handler import DBBaseHandler

UPSERT_BATCH_SIZE = 500


class CatalogGameInput(TypedDict):
    igdb_id: int
    name: str
    slug: str | None
    summary: str | None
    release_year: int | None
    first_release_date: int | None
    cover_image_id: str | None
    screenshot_image_ids: list[str]
    genres: list[str]
    platform_slugs: list[str]
    rating: float | None
    rating_count: int
    youtube_video_id: str | None
    igdb_url: str | None
    source_updated_at: int | None


class CatalogOrderBy(enum.StrEnum):
    RATING = "rating"
    NAME = "name"
    RELEASE_YEAR = "release_year"
    RATING_COUNT = "rating_count"
    # When the newest download source was recorded; games without one sort last.
    ADDED = "added"
    # The requesting user's most recent play activity; needs `played_by`.
    LAST_PLAYED = "last_played"


class CatalogOrderDir(enum.StrEnum):
    ASC = "asc"
    DESC = "desc"


class CatalogGameMatch(TypedDict):
    game: CatalogGame
    sources: list[GameSource]


class CatalogFacetCount(TypedDict):
    value: str
    game_count: int
    owned_count: int


def _owned_games(
    platform_slug: str | None = None, exclude_platform_slugs: list[str] | None = None
):
    """Catalog game ids with a source on an enabled host, optionally for one platform."""
    query = (
        select(GameSource.catalog_game_id)
        .join(GameHost, GameHost.id == GameSource.host_id)
        .where(GameHost.enabled.is_(True))
    )
    if platform_slug:
        query = query.where(GameSource.platform_slug == platform_slug)
    if exclude_platform_slugs:
        query = query.where(GameSource.platform_slug.not_in(exclude_platform_slugs))
    return query


def _sync_children[T](
    current: list[T],
    wanted: set[str],
    *,
    key: Callable[[T], str],
    build: Callable[[str], T],
) -> None:
    """Diff a child collection against the wanted keys, so unchanged rows stay put."""
    present = {key(child) for child in current}
    current[:] = [child for child in current if key(child) in wanted]
    current.extend(build(value) for value in sorted(wanted - present))


class DBCatalogHandler(DBBaseHandler):
    @begin_session
    def upsert_games(
        self,
        games: Sequence[CatalogGameInput],
        session: Session = None,  # type: ignore
    ) -> int:
        """Insert or update catalog games by IGDB id, replacing their platforms and genres."""
        written = 0
        for start in range(0, len(games), UPSERT_BATCH_SIZE):
            batch = games[start : start + UPSERT_BATCH_SIZE]
            existing = {
                game.igdb_id: game
                for game in session.scalars(
                    select(CatalogGame).where(
                        CatalogGame.igdb_id.in_([g["igdb_id"] for g in batch])
                    )
                )
            }
            for data in batch:
                game = existing.get(data["igdb_id"])
                if game is None:
                    game = CatalogGame(igdb_id=data["igdb_id"])
                    session.add(game)
                game.name = data["name"]
                game.slug = data["slug"]
                game.summary = data["summary"]
                game.release_year = data["release_year"]
                game.first_release_date = data["first_release_date"]
                game.cover_image_id = data["cover_image_id"]
                game.screenshot_image_ids = list(data["screenshot_image_ids"])
                game.rating = data["rating"]
                game.rating_count = data["rating_count"]
                game.youtube_video_id = data["youtube_video_id"]
                game.igdb_url = data["igdb_url"]
                game.source_updated_at = data["source_updated_at"]
                _sync_children(
                    game.platforms,
                    set(data["platform_slugs"]),
                    key=lambda p: p.platform_slug,
                    build=lambda slug: CatalogGamePlatform(platform_slug=slug),
                )
                _sync_children(
                    game.genre_links,
                    set(data["genres"]),
                    key=lambda g: g.genre,
                    build=lambda genre: CatalogGameGenre(genre=genre),
                )
                written += 1
            session.flush()
        return written

    @begin_session
    def get_game_by_igdb_id(
        self,
        igdb_id: int,
        session: Session = None,  # type: ignore
    ) -> CatalogGameMatch | None:
        game = session.scalar(
            select(CatalogGame).where(CatalogGame.igdb_id == igdb_id).limit(1)
        )
        if game is None:
            return None
        sources = self._sources_by_game(session, [game.id])
        return {"game": game, "sources": sources.get(game.id, [])}

    @begin_session
    def get_games_of_platform(
        self,
        platform_slug: str,
        session: Session = None,  # type: ignore
    ) -> list[CatalogGame]:
        return list(
            session.scalars(
                select(CatalogGame)
                .join(
                    CatalogGamePlatform,
                    CatalogGamePlatform.catalog_game_id == CatalogGame.id,
                )
                .where(CatalogGamePlatform.platform_slug == platform_slug)
                .order_by(CatalogGame.id)
            )
        )

    @begin_session
    def get_games(
        self,
        *,
        search: str | None = None,
        platform_slug: str | None = None,
        exclude_platform_slugs: list[str] | None = None,
        genre: str | None = None,
        min_rating: float | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        owned: bool | None = None,
        owned_platforms: bool | None = None,
        collection_id: int | None = None,
        played_by: int | None = None,
        order_by: CatalogOrderBy = CatalogOrderBy.RATING,
        order_dir: CatalogOrderDir = CatalogOrderDir.DESC,
        limit: int = 50,
        offset: int = 0,
        session: Session = None,  # type: ignore
    ) -> tuple[list[CatalogGameMatch], int]:
        query: Select = select(CatalogGame)

        if search:
            for word in search.split():
                query = query.where(CatalogGame.name.ilike(f"%{word}%"))
        if platform_slug:
            query = query.where(
                CatalogGame.id.in_(
                    select(CatalogGamePlatform.catalog_game_id).where(
                        CatalogGamePlatform.platform_slug == platform_slug
                    )
                )
            )
        if exclude_platform_slugs:
            # Keep games that still have at least one platform the user shows.
            query = query.where(
                CatalogGame.id.in_(
                    select(CatalogGamePlatform.catalog_game_id).where(
                        CatalogGamePlatform.platform_slug.not_in(exclude_platform_slugs)
                    )
                )
            )
        if genre:
            query = query.where(
                CatalogGame.id.in_(
                    select(CatalogGameGenre.catalog_game_id).where(
                        CatalogGameGenre.genre == genre
                    )
                )
            )
        if min_rating is not None:
            query = query.where(CatalogGame.rating >= min_rating)
        if year_from is not None:
            query = query.where(CatalogGame.release_year >= year_from)
        if year_to is not None:
            query = query.where(CatalogGame.release_year <= year_to)
        if owned_platforms:
            query = query.where(
                CatalogGame.id.in_(
                    select(CatalogGamePlatform.catalog_game_id).where(
                        CatalogGamePlatform.platform_slug.in_(
                            select(GameSource.platform_slug).distinct()
                        )
                    )
                )
            )
        if collection_id is not None:
            query = query.where(
                CatalogGame.id.in_(
                    select(CollectionGame.catalog_game_id).where(
                        CollectionGame.collection_id == collection_id
                    )
                )
            )
        if played_by is not None:
            query = query.where(
                CatalogGame.id.in_(
                    select(GamePlaySession.catalog_game_id).where(
                        GamePlaySession.user_id == played_by
                    )
                )
            )
        # Owning a game on one platform does not make it owned on another.
        owned_games = _owned_games(platform_slug, exclude_platform_slugs)
        if owned is True:
            query = query.where(CatalogGame.id.in_(owned_games))
        elif owned is False:
            query = query.where(CatalogGame.id.not_in(owned_games))

        total = session.scalar(select(func.count()).select_from(query.subquery()))

        query = query.order_by(*self._order_clauses(order_by, order_dir, played_by))
        games = list(session.scalars(query.offset(offset).limit(limit)))
        sources = self._sources_by_game(session, [game.id for game in games])
        return [
            {"game": game, "sources": sources.get(game.id, [])} for game in games
        ], total or 0

    @begin_session
    def get_platform_counts(
        self,
        session: Session = None,  # type: ignore
    ) -> list[CatalogFacetCount]:
        owned_on_platform = (
            select(GameSource.id)
            .join(GameHost, GameHost.id == GameSource.host_id)
            .where(
                GameHost.enabled.is_(True),
                GameSource.catalog_game_id == CatalogGamePlatform.catalog_game_id,
                GameSource.platform_slug == CatalogGamePlatform.platform_slug,
            )
            .exists()
        )
        owned_flag = case((owned_on_platform, 1), else_=0)
        rows = session.execute(
            select(
                CatalogGamePlatform.platform_slug,
                func.count(CatalogGamePlatform.catalog_game_id),
                func.sum(owned_flag),
            )
            .group_by(CatalogGamePlatform.platform_slug)
            .order_by(CatalogGamePlatform.platform_slug)
        ).all()
        return [
            {"value": slug, "game_count": count, "owned_count": int(owned_count or 0)}
            for slug, count, owned_count in rows
        ]

    @begin_session
    def get_genre_counts(
        self,
        session: Session = None,  # type: ignore
    ) -> list[CatalogFacetCount]:
        rows = session.execute(
            select(CatalogGameGenre.genre, func.count(CatalogGameGenre.catalog_game_id))
            .group_by(CatalogGameGenre.genre)
            .order_by(CatalogGameGenre.genre)
        ).all()
        return [
            {"value": genre, "game_count": count, "owned_count": 0}
            for genre, count in rows
        ]

    @begin_session
    def get_totals(
        self,
        session: Session = None,  # type: ignore
    ) -> tuple[int, int]:
        """Return (catalog size, games with a download source)."""
        total = session.scalar(select(func.count(CatalogGame.id))) or 0
        owned = (
            session.scalar(
                select(func.count(func.distinct(GameSource.catalog_game_id)))
                .join(GameHost, GameHost.id == GameSource.host_id)
                .where(GameHost.enabled.is_(True))
            )
            or 0
        )
        return total, owned

    @staticmethod
    def _order_clauses(
        order_by: CatalogOrderBy,
        order_dir: CatalogOrderDir,
        played_by: int | None = None,
    ) -> list:
        added_at = (
            select(func.max(GameSource.created_at))
            .where(GameSource.catalog_game_id == CatalogGame.id)
            .scalar_subquery()
        )
        last_played = (
            select(func.max(GamePlaySession.last_activity_at))
            .where(
                GamePlaySession.catalog_game_id == CatalogGame.id,
                GamePlaySession.user_id == (played_by if played_by is not None else -1),
            )
            .scalar_subquery()
        )
        column = {
            CatalogOrderBy.RATING: CatalogGame.rating,
            CatalogOrderBy.NAME: CatalogGame.name,
            CatalogOrderBy.RELEASE_YEAR: CatalogGame.release_year,
            CatalogOrderBy.RATING_COUNT: CatalogGame.rating_count,
            CatalogOrderBy.ADDED: added_at,
            CatalogOrderBy.LAST_PLAYED: last_played,
        }[order_by]
        direction = column.desc() if order_dir == CatalogOrderDir.DESC else column.asc()
        # NULLS LAST is not portable across MariaDB/MySQL/PostgreSQL, so sort a
        # null flag first; the rating tiebreak keeps popular games ahead.
        return [
            case((column.is_(None), 1), else_=0),
            direction,
            CatalogGame.rating_count.desc(),
            CatalogGame.id.asc(),
        ]

    @staticmethod
    def _sources_by_game(
        session: Session, game_ids: Sequence[int]
    ) -> dict[int, list[GameSource]]:
        if not game_ids:
            return {}
        grouped: dict[int, list[GameSource]] = defaultdict(list)
        for source in session.scalars(
            select(GameSource)
            .join(GameHost, GameHost.id == GameSource.host_id)
            .where(GameSource.catalog_game_id.in_(game_ids), GameHost.enabled.is_(True))
            .order_by(GameSource.id)
        ):
            grouped[source.catalog_game_id].append(source)
        return grouped
