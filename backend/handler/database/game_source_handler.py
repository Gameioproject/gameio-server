from collections.abc import Sequence
from typing import Any, TypedDict

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from decorators.database import begin_session
from models.base import utc_now
from models.game_source import GameHost, GameHostKind, GameSource

from .base_handler import DBBaseHandler


class GameSourceInput(TypedDict):
    catalog_game_id: int
    path: str
    filename: str
    platform_slug: str
    size: int | None
    md5: str | None
    sha1: str | None
    region: str | None


class DBGameSourceHandler(DBBaseHandler):
    # --- Hosts -------------------------------------------------------------

    @begin_session
    def add_host(
        self,
        *,
        name: str,
        kind: GameHostKind,
        base: str,
        platform_slug: str | None = None,
        enabled: bool = True,
        session: Session = None,  # type: ignore
    ) -> GameHost:
        host = GameHost(
            name=name,
            kind=kind,
            base=base,
            platform_slug=platform_slug,
            enabled=enabled,
        )
        session.add(host)
        session.flush()
        session.refresh(host)
        return host

    @begin_session
    def update_host(
        self,
        host_id: int,
        *,
        name: str | None = None,
        base: str | None = None,
        platform_slug: str | None = None,
        enabled: bool | None = None,
        session: Session = None,  # type: ignore
    ) -> GameHost | None:
        host = session.get(GameHost, host_id)
        if host is None:
            return None
        if name is not None:
            host.name = name
        if base is not None:
            host.base = base
        if platform_slug is not None:
            host.platform_slug = platform_slug or None
        if enabled is not None:
            host.enabled = enabled
        session.flush()
        session.refresh(host)
        return host

    @begin_session
    def get_host_by_base(
        self,
        kind: GameHostKind,
        base: str,
        session: Session = None,  # type: ignore
    ) -> GameHost | None:
        return session.scalar(
            select(GameHost).where(GameHost.kind == kind, GameHost.base == base)
        )

    @begin_session
    def mark_index_started(
        self, host_id: int, session: Session = None  # type: ignore
    ) -> None:
        host = session.get(GameHost, host_id)
        if host is not None:
            host.index_started_at = utc_now()

    @begin_session
    def mark_index_finished(
        self,
        host_id: int,
        stats: dict[str, Any] | None,
        session: Session = None,  # type: ignore
    ) -> None:
        host = session.get(GameHost, host_id)
        if host is None:
            return
        host.index_started_at = None
        if stats is not None:
            host.last_indexed_at = utc_now()
            host.last_index_stats = stats

    @begin_session
    def get_hosts(self, session: Session = None) -> list[GameHost]:  # type: ignore
        return list(session.scalars(select(GameHost).order_by(GameHost.id)))

    @begin_session
    def get_host(
        self, host_id: int, session: Session = None  # type: ignore
    ) -> GameHost | None:
        return session.get(GameHost, host_id)

    @begin_session
    def delete_host(self, host_id: int, session: Session = None) -> bool:  # type: ignore
        host = session.get(GameHost, host_id)
        if host is None:
            return False
        session.delete(host)
        return True

    # --- Sources -----------------------------------------------------------

    @begin_session
    def upsert_sources(
        self,
        host_id: int,
        sources: Sequence[GameSourceInput],
        session: Session = None,  # type: ignore
    ) -> tuple[int, int]:
        """Insert or update sources of one host keyed by path. Returns (created, updated)."""
        existing = {
            source.path: source
            for source in session.scalars(
                select(GameSource).where(
                    GameSource.host_id == host_id,
                    GameSource.path.in_([s["path"] for s in sources]),
                )
            )
        }
        created = updated = 0
        for data in sources:
            source = existing.get(data["path"])
            if source is None:
                source = GameSource(host_id=host_id, path=data["path"])
                session.add(source)
                created += 1
            else:
                updated += 1
            source.catalog_game_id = data["catalog_game_id"]
            source.filename = data["filename"]
            source.platform_slug = data["platform_slug"]
            source.size = data["size"]
            source.md5 = data["md5"]
            source.sha1 = data["sha1"]
            source.region = data["region"]
        session.flush()
        return created, updated

    @begin_session
    def get_source(
        self, source_id: int, session: Session = None  # type: ignore
    ) -> GameSource | None:
        return session.get(GameSource, source_id)

    @begin_session
    def get_source_by_path(
        self, host_id: int, path: str, session: Session = None  # type: ignore
    ) -> GameSource | None:
        return session.scalar(
            select(GameSource).where(
                GameSource.host_id == host_id, GameSource.path == path
            )
        )

    @begin_session
    def get_sources_for_game(
        self, catalog_game_id: int, session: Session = None  # type: ignore
    ) -> list[GameSource]:
        return list(
            session.scalars(
                select(GameSource)
                .where(GameSource.catalog_game_id == catalog_game_id)
                .order_by(GameSource.id)
            )
        )

    @begin_session
    def delete_source(self, source_id: int, session: Session = None) -> bool:  # type: ignore
        result = session.execute(delete(GameSource).where(GameSource.id == source_id))
        return bool(result.rowcount)

    @begin_session
    def delete_sources_of_host(
        self, host_id: int, session: Session = None  # type: ignore
    ) -> int:
        result = session.execute(
            delete(GameSource).where(GameSource.host_id == host_id)
        )
        return result.rowcount or 0

    @begin_session
    def count_sources_by_host(
        self, session: Session = None  # type: ignore
    ) -> dict[int, int]:
        rows = session.execute(
            select(GameSource.host_id, func.count(GameSource.id)).group_by(
                GameSource.host_id
            )
        ).all()
        return {host_id: count for host_id, count in rows}
