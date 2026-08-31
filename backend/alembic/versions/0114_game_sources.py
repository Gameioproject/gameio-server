"""Remote hosts and per-game download sources; owning a game means having a source.

Revision ID: 0114_game_sources
Revises: 0113_catalog_games
Create Date: 2026-08-29 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

from utils.database import CustomJSON

# revision identifiers, used by Alembic.
revision = "0114_game_sources"
down_revision = "0113_catalog_games"
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
        "game_hosts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column(
            "kind",
            sa.Enum("INTERNET_ARCHIVE", "HTTP", name="gamehostkind"),
            nullable=False,
        ),
        sa.Column("base", sa.String(length=1000), nullable=False),
        sa.Column("platform_slug", sa.String(length=100), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("index_started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_indexed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_index_stats", CustomJSON(), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )

    op.create_table(
        "game_sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("catalog_game_id", sa.Integer(), nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(length=1000), nullable=False),
        sa.Column("filename", sa.String(length=500), nullable=False),
        sa.Column("platform_slug", sa.String(length=100), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=True),
        sa.Column("md5", sa.String(length=32), nullable=True),
        sa.Column("sha1", sa.String(length=40), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["catalog_game_id"], ["catalog_games.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["host_id"], ["game_hosts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    # MariaDB: UNIQUE(host_id, path) is 4004 bytes in utf8mb4, over InnoDB's
    # 3072-byte B-tree limit, so it degrades to a HASH index. A hash index
    # cannot back a foreign key, which breaks the host_id FK (errno 150).
    # Create an explicit B-tree index on host_id first so the FK has one,
    # then add the unique constraint (still enforced on the full value).
    op.create_index(
        "idx_game_sources_host",
        "game_sources",
        ["host_id"],
        if_not_exists=True,
    )
    op.create_index(
        "unique_game_source_host_path",
        "game_sources",
        ["host_id", "path"],
        unique=True,
        if_not_exists=True,
    )
    op.create_index(
        "idx_game_sources_game",
        "game_sources",
        ["catalog_game_id", "id"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("game_sources")
    op.drop_table("game_hosts")
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS gamehostkind")
