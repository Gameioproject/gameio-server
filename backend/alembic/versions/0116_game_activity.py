"""Play sessions and saved data keyed by catalog game, shared across devices.

Revision ID: 0116_game_activity
Revises: 0115_collection_games
Create Date: 2026-08-29 18:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0116_game_activity"
down_revision = "0115_collection_games"
branch_labels = None
depends_on = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "game_play_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("catalog_game_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.String(length=100), nullable=True),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("last_activity_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("ended_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "duration_seconds",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["catalog_game_id"], ["catalog_games.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_index(
        "idx_game_play_sessions_user_game",
        "game_play_sessions",
        ["user_id", "catalog_game_id"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_game_play_sessions_user_activity",
        "game_play_sessions",
        ["user_id", "last_activity_at"],
        if_not_exists=True,
    )

    op.create_table(
        "game_assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("catalog_game_id", sa.Integer(), nullable=False),
        sa.Column(
            "kind", sa.Enum("SAVE", "STATE", name="gameassetkind"), nullable=False
        ),
        sa.Column("emulator", sa.String(length=100), nullable=False, server_default=""),
        sa.Column("file_name", sa.String(length=400), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("screenshot", sa.LargeBinary(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["catalog_game_id"], ["catalog_games.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "catalog_game_id",
            "kind",
            "emulator",
            "file_name",
            name="unique_game_asset",
        ),
        if_not_exists=True,
    )
    op.create_index(
        "idx_game_assets_user_game",
        "game_assets",
        ["user_id", "catalog_game_id", "kind"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("game_assets")
    op.drop_table("game_play_sessions")
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS gameassetkind")
