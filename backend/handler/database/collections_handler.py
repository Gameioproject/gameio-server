import functools
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import (
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.orm import (
    Query,
    QueryableAttribute,
    Session,
    load_only,
)

from decorators.database import begin_session
from models.catalog import CatalogGame
from models.collection import Collection, CollectionGame

from .base_handler import DBBaseHandler


def with_games(func):
    """Inject the base collection query; `games` loads eagerly via selectin."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        kwargs["query"] = select(Collection)
        return func(*args, **kwargs)

    return wrapper


class DBCollectionsHandler(DBBaseHandler):
    @begin_session
    @with_games
    def add_collection(
        self,
        collection: Collection,
        query: Query = None,  # type: ignore
        session: Session = None,  # type: ignore
    ) -> Collection:
        collection = session.merge(collection)
        session.flush()

        return session.scalar(query.filter_by(id=collection.id).limit(1))

    @begin_session
    @with_games
    def get_collection(
        self,
        id: int,
        query: Query = None,  # type: ignore
        session: Session = None,  # type: ignore
    ) -> Collection | None:
        return session.scalar(query.filter_by(id=id).limit(1))

    @begin_session
    @with_games
    def get_collection_by_name(
        self,
        name: str,
        user_id: int,
        query: Query = None,  # type: ignore
        session: Session = None,  # type: ignore
    ) -> Collection | None:
        return session.scalar(query.filter_by(name=name, user_id=user_id).limit(1))

    @begin_session
    @with_games
    def get_favorite_collection(
        self,
        user_id: int,
        query: Query = None,  # type: ignore
        session: Session = None,  # type: ignore
    ) -> Collection | None:
        return session.scalar(
            query.filter_by(is_favorite=True, user_id=user_id).limit(1)
        )

    @begin_session
    @with_games
    def get_collections(
        self,
        updated_after: datetime | None = None,
        only_fields: Sequence[QueryableAttribute] | None = None,
        query: Query = None,  # type: ignore
        session: Session = None,  # type: ignore
    ) -> Sequence[Collection]:
        if updated_after:
            query = query.filter(Collection.updated_at > updated_after)

        if only_fields:
            query = query.options(load_only(*only_fields))

        return session.scalars(query.order_by(Collection.name.asc())).unique().all()

    @begin_session
    @with_games
    def update_collection(
        self,
        id: int,
        data: dict,
        query: Query = None,  # type: ignore
        session: Session = None,  # type: ignore
    ) -> Collection:
        session.execute(
            update(Collection)
            .where(Collection.id == id)
            .values(**data)
            .execution_options(synchronize_session="evaluate")
        )

        return session.scalar(query.filter_by(id=id).limit(1))

    @begin_session
    @with_games
    def add_games_to_collection(
        self,
        id: int,
        igdb_ids: list[int],
        query: Query = None,  # type: ignore
        session: Session = None,  # type: ignore
    ) -> Collection:
        game_ids = set(
            session.scalars(
                select(CatalogGame.id).where(CatalogGame.igdb_id.in_(igdb_ids))
            ).all()
        )
        existing = set(
            session.scalars(
                select(CollectionGame.catalog_game_id).where(
                    CollectionGame.collection_id == id
                )
            ).all()
        )
        new_ids = game_ids - existing
        if new_ids:
            session.execute(
                insert(CollectionGame),
                [{"collection_id": id, "catalog_game_id": gid} for gid in new_ids],
            )
            self._touch(session, id)
        session.expire_all()
        return session.scalar(query.filter_by(id=id).limit(1))

    @begin_session
    @with_games
    def remove_games_from_collection(
        self,
        id: int,
        igdb_ids: list[int],
        query: Query = None,  # type: ignore
        session: Session = None,  # type: ignore
    ) -> Collection:
        result = session.execute(
            delete(CollectionGame).where(
                CollectionGame.collection_id == id,
                CollectionGame.catalog_game_id.in_(
                    select(CatalogGame.id).where(CatalogGame.igdb_id.in_(igdb_ids))
                ),
            )
        )
        if result.rowcount > 0:
            self._touch(session, id)
        session.expire_all()
        return session.scalar(query.filter_by(id=id).limit(1))

    @begin_session
    def get_favorite_igdb_ids(
        self, user_id: int, session: Session = None  # type: ignore
    ) -> set[int]:
        return set(
            session.scalars(
                select(CatalogGame.igdb_id)
                .join(CollectionGame, CollectionGame.catalog_game_id == CatalogGame.id)
                .join(Collection, Collection.id == CollectionGame.collection_id)
                .where(Collection.is_favorite.is_(True), Collection.user_id == user_id)
            ).all()
        )

    @staticmethod
    def _touch(session: Session, collection_id: int) -> None:
        session.execute(
            update(Collection)
            .where(Collection.id == collection_id)
            .values(updated_at=datetime.now(timezone.utc))
            .execution_options(synchronize_session="evaluate")
        )

    @begin_session
    def delete_collection(
        self,
        id: int,
        session: Session = None,  # type: ignore
    ) -> None:
        session.execute(
            delete(Collection)
            .where(Collection.id == id)
            .execution_options(synchronize_session="evaluate")
        )
