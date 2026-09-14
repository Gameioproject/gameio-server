"""Catalog conversations, likes, reports, and personal author blocks."""

import sqlalchemy as sa
from alembic import op

revision = "0123_game_comments"
down_revision = "0122_source_file_index"
branch_labels = None
depends_on = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            name,
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        for name in ("created_at", "updated_at")
    ]


def upgrade() -> None:
    op.create_table(
        "game_comments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "catalog_game_id",
            sa.Integer(),
            sa.ForeignKey("catalog_games.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "parent_id",
            sa.Integer(),
            sa.ForeignKey("game_comments.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("spoiler", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("edited_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        *_timestamps(),
        if_not_exists=True,
    )
    op.create_index(
        "idx_game_comments_game_parent_created",
        "game_comments",
        ["catalog_game_id", "parent_id", "created_at", "id"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_game_comments_parent",
        "game_comments",
        ["parent_id", "deleted_at"],
        if_not_exists=True,
    )
    op.create_index(
        "ix_game_comments_user_id", "game_comments", ["user_id"], if_not_exists=True
    )
    op.create_table(
        "game_comment_likes",
        sa.Column(
            "comment_id",
            sa.Integer(),
            sa.ForeignKey("game_comments.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        *_timestamps(),
        if_not_exists=True,
    )
    op.create_index(
        "ix_game_comment_likes_user_id",
        "game_comment_likes",
        ["user_id"],
        if_not_exists=True,
    )
    op.create_table(
        "game_comment_reports",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "comment_id",
            sa.Integer(),
            sa.ForeignKey("game_comments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("body_snapshot", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column(
            "resolved_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.UniqueConstraint("comment_id", "user_id", name="unique_game_comment_report"),
        *_timestamps(),
        if_not_exists=True,
    )
    op.create_index(
        "idx_game_comment_reports_status_created",
        "game_comment_reports",
        ["status", "created_at"],
        if_not_exists=True,
    )
    op.create_index(
        "ix_game_comment_reports_user_id",
        "game_comment_reports",
        ["user_id"],
        if_not_exists=True,
    )
    op.create_table(
        "game_comment_blocks",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "blocked_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        *_timestamps(),
        if_not_exists=True,
    )
    op.create_index(
        "ix_game_comment_blocks_blocked_user_id",
        "game_comment_blocks",
        ["blocked_user_id"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("game_comment_blocks", if_exists=True)
    op.drop_table("game_comment_reports", if_exists=True)
    op.drop_table("game_comment_likes", if_exists=True)
    op.drop_table("game_comments", if_exists=True)
