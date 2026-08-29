"""Metadata catalog of games that may or may not exist in the library.

Revision ID: 0113_catalog_games
Revises: 0112_publisher_developer_split
Create Date: 2026-08-29 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

from utils.database import CustomJSON

# revision identifiers, used by Alembic.
revision = "0113_catalog_games"
down_revision = "0112_publisher_developer_split"
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
        "catalog_games",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("igdb_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=400), nullable=False),
        sa.Column("slug", sa.String(length=400), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("release_year", sa.Integer(), nullable=True),
        sa.Column("first_release_date", sa.Integer(), nullable=True),
        sa.Column("cover_image_id", sa.String(length=64), nullable=True),
        sa.Column("screenshot_image_ids", CustomJSON(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column(
            "rating_count", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column("youtube_video_id", sa.String(length=64), nullable=True),
        sa.Column("igdb_url", sa.String(length=1000), nullable=True),
        sa.Column("source_updated_at", sa.Integer(), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("igdb_id", name="unique_catalog_games_igdb_id"),
        if_not_exists=True,
    )
    op.create_index(
        "idx_catalog_games_name", "catalog_games", ["name"], if_not_exists=True
    )
    op.create_index(
        "idx_catalog_games_rating",
        "catalog_games",
        ["rating", "rating_count"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_catalog_games_release_year",
        "catalog_games",
        ["release_year"],
        if_not_exists=True,
    )

    op.create_table(
        "catalog_game_platforms",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("catalog_game_id", sa.Integer(), nullable=False),
        sa.Column("platform_slug", sa.String(length=100), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["catalog_game_id"], ["catalog_games.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "catalog_game_id", "platform_slug", name="unique_catalog_game_platform"
        ),
        if_not_exists=True,
    )
    op.create_index(
        "idx_catalog_game_platforms_slug",
        "catalog_game_platforms",
        ["platform_slug", "catalog_game_id"],
        if_not_exists=True,
    )

    op.create_table(
        "catalog_game_genres",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("catalog_game_id", sa.Integer(), nullable=False),
        sa.Column("genre", sa.String(length=100), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["catalog_game_id"], ["catalog_games.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "catalog_game_id", "genre", name="unique_catalog_game_genre"
        ),
        if_not_exists=True,
    )
    op.create_index(
        "idx_catalog_game_genres_genre",
        "catalog_game_genres",
        ["genre", "catalog_game_id"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("catalog_game_genres")
    op.drop_table("catalog_game_platforms")
    op.drop_table("catalog_games")
