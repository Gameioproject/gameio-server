"""Content encoding on game assets, so save files and states can be stored gzipped.

Existing rows keep a null encoding and stay raw; they are compressed the next time
their unit is uploaded.

Revision ID: 0124_asset_content_encoding
Revises: 0123_game_comments
Create Date: 2026-09-30 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "0124_asset_content_encoding"
down_revision = "0123_game_comments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("game_assets") as batch_op:
        batch_op.add_column(
            sa.Column("content_encoding", sa.String(length=16), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("game_assets") as batch_op:
        batch_op.drop_column("content_encoding")
