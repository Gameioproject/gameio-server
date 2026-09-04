from collections.abc import Sequence
from datetime import datetime
from typing import TypedDict

import hashlib

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from decorators.database import begin_session
from models.base import utc_now
from models.catalog import CatalogGame
from models.game_activity import (
    DEFAULT_CHANNEL,
    GameAsset,
    GameAssetKind,
    GamePlaySession,
    asset_unit_key,
)

from .base_handler import DBBaseHandler


class PlayStats(TypedDict):
    last_played_at: object
    play_time_seconds: int


class DBGameActivityHandler(DBBaseHandler):
    # --- Play sessions -----------------------------------------------------

    @begin_session
    def start_session(
        self,
        *,
        user_id: int,
        catalog_game_id: int,
        device_id: str | None,
        session: Session = None,  # type: ignore
    ) -> GamePlaySession:
        now = utc_now()
        play = GamePlaySession(
            user_id=user_id,
            catalog_game_id=catalog_game_id,
            device_id=device_id,
            started_at=now,
            last_activity_at=now,
        )
        session.add(play)
        session.flush()
        session.refresh(play)
        return play

    @begin_session
    def get_session(
        self, session_id: int, session: Session = None  # type: ignore
    ) -> GamePlaySession | None:
        return session.get(GamePlaySession, session_id)

    @begin_session
    def record_session(
        self,
        *,
        user_id: int,
        catalog_game_id: int,
        device_id: str | None,
        started_at: datetime,
        ended_at: datetime,
        duration_seconds: int,
        session: Session = None,  # type: ignore
    ) -> GamePlaySession:
        """A finished sitting reported after the fact by a client."""
        play = GamePlaySession(
            user_id=user_id,
            catalog_game_id=catalog_game_id,
            device_id=device_id,
            started_at=started_at,
            last_activity_at=ended_at,
            ended_at=ended_at,
            duration_seconds=duration_seconds,
        )
        session.add(play)
        session.flush()
        session.refresh(play)
        return play

    @begin_session
    def touch_session(
        self,
        session_id: int,
        *,
        end: bool = False,
        session: Session = None,  # type: ignore
    ) -> GamePlaySession | None:
        """Record activity; the duration is the wall time between start and last activity."""
        play = session.get(GamePlaySession, session_id)
        if play is None or play.ended_at is not None:
            return play
        now = utc_now()
        play.last_activity_at = now
        play.duration_seconds = int((now - play.started_at).total_seconds())
        if end:
            play.ended_at = now
        session.flush()
        session.refresh(play)
        return play

    @begin_session
    def get_play_stats(
        self,
        user_id: int,
        catalog_game_ids: Sequence[int],
        session: Session = None,  # type: ignore
    ) -> dict[int, PlayStats]:
        if not catalog_game_ids:
            return {}
        rows = session.execute(
            select(
                GamePlaySession.catalog_game_id,
                func.max(GamePlaySession.last_activity_at),
                func.sum(GamePlaySession.duration_seconds),
            )
            .where(
                GamePlaySession.user_id == user_id,
                GamePlaySession.catalog_game_id.in_(catalog_game_ids),
            )
            .group_by(GamePlaySession.catalog_game_id)
        ).all()
        return {
            game_id: {"last_played_at": last, "play_time_seconds": int(total or 0)}
            for game_id, last, total in rows
        }

    # --- Saves and states ---------------------------------------------------

    @begin_session
    def list_assets(
        self,
        *,
        user_id: int,
        catalog_game_id: int,
        kind: GameAssetKind | None = None,
        emulator: str | None = None,
        session: Session = None,  # type: ignore
    ) -> list[GameAsset]:
        query = select(GameAsset).where(
            GameAsset.user_id == user_id, GameAsset.catalog_game_id == catalog_game_id
        )
        if kind is not None:
            query = query.where(GameAsset.kind == kind)
        if emulator is not None:
            query = query.where(GameAsset.emulator == emulator)
        return list(session.scalars(query.order_by(GameAsset.updated_at.desc())))

    @begin_session
    def list_user_assets(
        self,
        *,
        user_id: int,
        kind: GameAssetKind,
        session: Session = None,  # type: ignore
    ) -> list[GameAsset]:
        return list(
            session.scalars(
                select(GameAsset)
                .where(GameAsset.user_id == user_id, GameAsset.kind == kind)
                .order_by(GameAsset.updated_at.desc())
            )
        )

    @begin_session
    def get_unit(
        self,
        *,
        user_id: int,
        catalog_game_id: int,
        unit_key: str,
        session: Session = None,  # type: ignore
    ) -> GameAsset | None:
        return session.scalar(
            select(GameAsset).where(
                GameAsset.user_id == user_id,
                GameAsset.catalog_game_id == catalog_game_id,
                GameAsset.unit_key == unit_key,
            )
        )

    @begin_session
    def list_assets_for_games(
        self,
        *,
        user_id: int,
        catalog_game_ids: Sequence[int],
        session: Session = None,  # type: ignore
    ) -> list[GameAsset]:
        if not catalog_game_ids:
            return []
        return list(
            session.scalars(
                select(GameAsset).where(
                    GameAsset.user_id == user_id,
                    GameAsset.catalog_game_id.in_(catalog_game_ids),
                )
            )
        )

    @begin_session
    def upsert_asset(
        self,
        *,
        user_id: int,
        catalog_game_id: int,
        kind: GameAssetKind,
        emulator: str,
        file_name: str,
        content: bytes,
        screenshot: bytes | None,
        channel: str = DEFAULT_CHANNEL,
        slot_number: int = 0,
        device_id: str | None = None,
        session: Session = None,  # type: ignore
    ) -> GameAsset:
        """Store the unit's current version, replacing whatever the unit held.

        The unit is the identity (docs/SAVE_SYNC.md); the file name follows the
        latest upload. Staleness against a base hash is the endpoint's business.
        """
        key = asset_unit_key(kind, emulator, channel, slot_number)
        asset = session.scalar(
            select(GameAsset).where(
                GameAsset.user_id == user_id,
                GameAsset.catalog_game_id == catalog_game_id,
                GameAsset.unit_key == key,
            )
        )
        if asset is None:
            asset = GameAsset(
                user_id=user_id,
                catalog_game_id=catalog_game_id,
                kind=kind,
                emulator=emulator,
                unit_key=key,
            )
            session.add(asset)
        asset.channel = channel
        asset.slot_number = slot_number if kind == GameAssetKind.STATE else 0
        asset.slot = channel if kind == GameAssetKind.SAVE else None
        asset.file_name = file_name
        asset.content_hash = hashlib.sha256(content).hexdigest()
        asset.content = content
        asset.size = len(content)
        if screenshot is not None:
            asset.screenshot = screenshot
        asset.updated_by_device_id = device_id
        asset.updated_at = utc_now()
        session.flush()
        session.refresh(asset)
        return asset

    @begin_session
    def get_asset(
        self, asset_id: int, session: Session = None  # type: ignore
    ) -> GameAsset | None:
        return session.get(GameAsset, asset_id)

    @begin_session
    def delete_asset(
        self, asset_id: int, user_id: int, session: Session = None  # type: ignore
    ) -> bool:
        result = session.execute(
            delete(GameAsset).where(
                GameAsset.id == asset_id, GameAsset.user_id == user_id
            )
        )
        return bool(result.rowcount)

    @begin_session
    def game_id_for_igdb(
        self, igdb_id: int, session: Session = None  # type: ignore
    ) -> int | None:
        return session.scalar(
            select(CatalogGame.id).where(CatalogGame.igdb_id == igdb_id)
        )
