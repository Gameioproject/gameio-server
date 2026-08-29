from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    Enum,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel
from models.catalog import CatalogGame

DEVICE_ID_MAX_LENGTH = 100
EMULATOR_MAX_LENGTH = 100
ASSET_FILE_NAME_MAX_LENGTH = 400


class GamePlaySession(BaseModel):
    """One sitting of a catalog game by a user, reported by any client."""

    __tablename__ = "game_play_sessions"
    __table_args__ = (
        Index("idx_game_play_sessions_user_game", "user_id", "catalog_game_id"),
        Index("idx_game_play_sessions_user_activity", "user_id", "last_activity_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    catalog_game_id: Mapped[int] = mapped_column(
        ForeignKey("catalog_games.id", ondelete="CASCADE")
    )
    device_id: Mapped[str | None] = mapped_column(String(length=DEVICE_ID_MAX_LENGTH))
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    last_activity_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)

    game: Mapped[CatalogGame] = relationship(lazy="joined")


class GameAssetKind(enum.StrEnum):
    SAVE = "save"
    STATE = "state"


class GameAsset(BaseModel):
    """A save file or save state, stored in the database so every device sees it."""

    __tablename__ = "game_assets"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "catalog_game_id",
            "kind",
            "emulator",
            "file_name",
            name="unique_game_asset",
        ),
        Index("idx_game_assets_user_game", "user_id", "catalog_game_id", "kind"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    catalog_game_id: Mapped[int] = mapped_column(
        ForeignKey("catalog_games.id", ondelete="CASCADE")
    )
    kind: Mapped[GameAssetKind] = mapped_column(Enum(GameAssetKind))
    # Core or emulator the asset belongs to; formats differ between them.
    emulator: Mapped[str] = mapped_column(
        String(length=EMULATOR_MAX_LENGTH), default=""
    )
    file_name: Mapped[str] = mapped_column(String(length=ASSET_FILE_NAME_MAX_LENGTH))
    content: Mapped[bytes] = mapped_column(LargeBinary)
    size: Mapped[int] = mapped_column(Integer, default=0)
    screenshot: Mapped[bytes | None] = mapped_column(LargeBinary)

    game: Mapped[CatalogGame] = relationship(lazy="joined")
