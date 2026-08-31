"""Slot and content hash on game assets, for the classic saves protocol.

Revision ID: 0118_asset_slot_hash
Revises: 0117_drop_rom_tables
Create Date: 2026-08-31 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "0118_asset_slot_hash"
down_revision = "0117_drop_rom_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "game_assets",
        sa.Column("slot", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "game_assets",
        sa.Column("content_hash", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("game_assets", "content_hash")
    op.drop_column("game_assets", "slot")
