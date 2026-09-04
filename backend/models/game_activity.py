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
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel
from models.catalog import CatalogGame

DEVICE_ID_MAX_LENGTH = 100
EMULATOR_MAX_LENGTH = 100
ASSET_FILE_NAME_MAX_LENGTH = 400
CHANNEL_MAX_LENGTH = 64
UNIT_KEY_MAX_LENGTH = 300
DEFAULT_CHANNEL = "autosave"


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


def asset_unit_key(
    kind: GameAssetKind, emulator: str, channel: str, slot_number: int
) -> str:
    """The identity of one sync unit within a user's game; see docs/SAVE_SYNC.md."""
    slot = slot_number if kind == GameAssetKind.STATE else 0
    return f"{kind.value}|{emulator}|{channel}|{slot}"


class GameAsset(BaseModel):
    """A save file or save state, stored in the database so every device sees it.

    One row per sync unit: (user, game, kind, emulator, channel, slot). There is no
    history; the row is the current version and `content_hash` is its identity for
    the reconcile rule.
    """

    __tablename__ = "game_assets"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "catalog_game_id",
            "unit_key",
            name="unique_game_asset_unit",
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
    # Legacy classic-protocol field: mirrors `channel` for saves, null for states.
    slot: Mapped[str | None] = mapped_column(String(length=64), default=None)
    channel: Mapped[str] = mapped_column(
        String(length=CHANNEL_MAX_LENGTH), default=DEFAULT_CHANNEL
    )
    # Launcher slot for states (-1 auto, 0-9 numbered, 100-109 quick ring); 0 for saves.
    slot_number: Mapped[int] = mapped_column(Integer, default=0)
    unit_key: Mapped[str] = mapped_column(String(length=UNIT_KEY_MAX_LENGTH))
    updated_by_device_id: Mapped[str | None] = mapped_column(
        String(length=DEVICE_ID_MAX_LENGTH), default=None
    )
    content_hash: Mapped[str | None] = mapped_column(String(length=64), default=None)
    # Plain LargeBinary is a 64 KB BLOB on MariaDB; a single N64 battery save is
    # already 290 KB and save states run to megabytes, so both blobs need the
    # long variant. The ceiling that actually applies is MAX_ASSET_BYTES.
    content: Mapped[bytes] = mapped_column(
        LargeBinary().with_variant(LONGBLOB, "mysql", "mariadb")
    )
    size: Mapped[int] = mapped_column(Integer, default=0)
    screenshot: Mapped[bytes | None] = mapped_column(
        LargeBinary().with_variant(LONGBLOB, "mysql", "mariadb")
    )

    game: Mapped[CatalogGame] = relationship(lazy="joined")
