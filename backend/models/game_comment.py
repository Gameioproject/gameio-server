from __future__ import annotations

from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel

COMMENT_BODY_MAX_LENGTH = 2000
COMMENT_REPORT_MAX_LENGTH = 500
COMMENT_PAGE_MAX_SIZE = 50


class GameComment(BaseModel):
    __tablename__ = "game_comments"
    __table_args__ = (
        Index(
            "idx_game_comments_game_parent_created",
            "catalog_game_id",
            "parent_id",
            "created_at",
            "id",
        ),
        Index("idx_game_comments_parent", "parent_id", "deleted_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    catalog_game_id: Mapped[int] = mapped_column(
        ForeignKey("catalog_games.id", ondelete="CASCADE")
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("game_comments.id", ondelete="CASCADE")
    )
    body: Mapped[str] = mapped_column(Text)
    spoiler: Mapped[bool] = mapped_column(default=False)
    edited_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


class GameCommentLike(BaseModel):
    __tablename__ = "game_comment_likes"

    comment_id: Mapped[int] = mapped_column(
        ForeignKey("game_comments.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True
    )


class GameCommentReport(BaseModel):
    __tablename__ = "game_comment_reports"
    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", name="unique_game_comment_report"),
        Index("idx_game_comment_reports_status_created", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("game_comments.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    reason: Mapped[str] = mapped_column(String(COMMENT_REPORT_MAX_LENGTH))
    body_snapshot: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    resolved_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )


class GameCommentBlock(BaseModel):
    __tablename__ = "game_comment_blocks"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    blocked_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True
    )
