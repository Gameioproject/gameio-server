"""Widen the game asset blobs from BLOB to LONGBLOB.

SQLAlchemy's bare LargeBinary maps to a 64 KB BLOB on MariaDB. Real saves pass
that immediately -- an N64 battery save is ~290 KB -- so every upload larger
than 64 KB failed with "Data too long for column 'content'". Screenshots hit the
same wall. LONGBLOB lifts the column ceiling above MAX_ASSET_BYTES, which is
where the limit belongs.

Revision ID: 0119_asset_longblob
Revises: 0118_asset_slot_hash
Create Date: 2026-09-01 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import LONGBLOB

revision = "0119_asset_longblob"
down_revision = "0118_asset_slot_hash"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("game_assets") as batch_op:
        batch_op.alter_column(
            "content",
            existing_type=sa.LargeBinary(),
            type_=LONGBLOB(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "screenshot",
            existing_type=sa.LargeBinary(),
            type_=LONGBLOB(),
            existing_nullable=True,
        )


def downgrade() -> None:
    # Narrowing truncates anything over 64 KB, so drop those rows first rather
    # than silently corrupting saves.
    op.execute("DELETE FROM game_assets WHERE LENGTH(content) > 65535")
    with op.batch_alter_table("game_assets") as batch_op:
        batch_op.alter_column(
            "content",
            existing_type=LONGBLOB(),
            type_=sa.LargeBinary(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "screenshot",
            existing_type=LONGBLOB(),
            type_=sa.LargeBinary(),
            existing_nullable=True,
        )
