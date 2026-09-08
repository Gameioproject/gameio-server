"""Torrent sources remember their file index, for "select only" (BEP 53) magnets.

Revision ID: 0122_source_file_index
Revises: 0121_torrent_hosts
Create Date: 2026-09-07 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0122_source_file_index"
down_revision = "0121_torrent_hosts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("game_sources", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("file_index", sa.Integer(), nullable=True), if_not_exists=True
        )


def downgrade() -> None:
    with op.batch_alter_table("game_sources", schema=None) as batch_op:
        batch_op.drop_column("file_index", if_exists=True)
