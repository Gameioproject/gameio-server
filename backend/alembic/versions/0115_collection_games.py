"""Collections hold catalog games, owned or not.

Revision ID: 0115_collection_games
Revises: 0114_game_sources
Create Date: 2026-08-29 14:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0115_collection_games"
down_revision = "0114_game_sources"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collections_games",
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("catalog_game_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["collection_id"], ["collections.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["catalog_game_id"], ["catalog_games.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("collection_id", "catalog_game_id"),
        if_not_exists=True,
    )
    op.create_index(
        "idx_collections_games_game",
        "collections_games",
        ["catalog_game_id", "collection_id"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("collections_games")
