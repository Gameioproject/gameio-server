"""Drop the ROM library tables: the server only keeps catalog metadata now.

Revision ID: 0117_drop_rom_tables
Revises: 0116_game_activity
Create Date: 2026-08-29 20:00:00.000000

"""

from alembic import op

from config import ROMM_DB_DRIVER

# revision identifiers, used by Alembic.
revision = "0117_drop_rom_tables"
down_revision = "0116_game_activity"
branch_labels = None
depends_on = None

VIEWS = ["virtual_collections", "sibling_roms", "roms_metadata"]

# Children before parents so every foreign key is gone before its target.
TABLES = [
    "play_sessions",
    "device_save_sync",
    "track_meta",
    "sync_sessions",
    "saves",
    "rom_file_user",
    "rom_file_doc_meta",
    "music_playlist_tracks",
    "music_favorite_tracks",
    "collections_roms",
    "virtual_collection_roms",
    "states",
    "smart_collections",
    "screenshots",
    "roms_facets",
    "rom_user",
    "rom_notes",
    "rom_files",
    "music_playlists",
    "roms",
    "firmware",
    "platforms",
]

POSTGRES_FUNCTIONS = [
    "romm_sync_rom_facets",
    "romm_sync_virtual_collection_roms",
    "romm_age_ratings",
    "romm_gamelist_epoch_ms",
]


def upgrade() -> None:
    for view in VIEWS:
        op.execute(f"DROP VIEW IF EXISTS {view}")
    for table in TABLES:
        op.execute(f"DROP TABLE IF EXISTS {table}")
    if ROMM_DB_DRIVER == "postgresql":
        for function in POSTGRES_FUNCTIONS:
            op.execute(f"DROP FUNCTION IF EXISTS {function} CASCADE")


def downgrade() -> None:
    # The library schema is gone for good; restoring it means restoring a backup.
    pass
