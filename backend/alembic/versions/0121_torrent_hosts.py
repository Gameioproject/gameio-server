"""Torrent game hosts: a third host kind, and the info hash learnt when indexing.

Revision ID: 0121_torrent_hosts
Revises: 0120_asset_units
Create Date: 2026-09-07 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from utils.database import is_postgresql

# revision identifiers, used by Alembic.
revision = "0121_torrent_hosts"
down_revision = "0120_asset_units"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    if is_postgresql(connection):
        with op.get_context().autocommit_block():
            op.execute("ALTER TYPE gamehostkind ADD VALUE IF NOT EXISTS 'TORRENT'")
        op.add_column(
            "game_hosts",
            sa.Column("info_hash", sa.String(length=40), nullable=True),
            if_not_exists=True,
        )
    else:
        kind_enum = sa.Enum("INTERNET_ARCHIVE", "HTTP", "TORRENT", name="gamehostkind")
        with op.batch_alter_table("game_hosts", schema=None) as batch_op:
            batch_op.alter_column("kind", type_=kind_enum, nullable=False)
            batch_op.add_column(
                sa.Column("info_hash", sa.String(length=40), nullable=True),
                if_not_exists=True,
            )


def downgrade() -> None:
    # PostgreSQL cannot remove an enum value; the column is the only thing taken back.
    with op.batch_alter_table("game_hosts", schema=None) as batch_op:
        batch_op.drop_column("info_hash", if_exists=True)
