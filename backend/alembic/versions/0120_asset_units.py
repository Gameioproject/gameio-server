"""One row per sync unit: channel, slot number and unit key on game assets.

Revision ID: 0120_asset_units
Revises: 0119_asset_longblob
Create Date: 2026-09-04 09:30:00.000000

Backfills the new columns from the classic-protocol fields (`slot` for saves, the
timestamped file name for states), collapses rows that now share a unit to the
newest one, and swaps the file-name unique index for the unit index.
"""

import re

import sqlalchemy as sa
from alembic import op

revision = "0120_asset_units"
down_revision = "0119_asset_longblob"
branch_labels = None
depends_on = None

_TS = r" \[\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\]"
_STATE_NAME = re.compile(
    r"^(?P<rom>.+?)(?:" + _TS + r")?(?:\.(?P<channel>[^.\[\]/]+?))?\.state(?:\.auto|(?P<n>\d+))?$",
    re.IGNORECASE,
)


def _state_identity(file_name: str) -> tuple[str, int]:
    m = _STATE_NAME.match(file_name)
    if not m:
        return "autosave", 0
    channel = m.group("channel") or "autosave"
    if file_name.lower().endswith(".state.auto"):
        return channel, -1
    return channel, int(m.group("n") or 0)


def upgrade() -> None:
    op.add_column(
        "game_assets",
        sa.Column("channel", sa.String(length=64), nullable=False, server_default="autosave"),
    )
    op.add_column(
        "game_assets",
        sa.Column("slot_number", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "game_assets",
        sa.Column("unit_key", sa.String(length=300), nullable=False, server_default=""),
    )
    op.add_column(
        "game_assets",
        sa.Column("updated_by_device_id", sa.String(length=100), nullable=True),
    )

    conn = op.get_bind()
    rows = conn.execute(
        sa.text("SELECT id, user_id, catalog_game_id, kind, emulator, slot, file_name, updated_at FROM game_assets")
    ).mappings().all()
    units: dict[tuple, list] = {}
    for r in rows:
        kind = str(r["kind"]).lower()
        if kind.endswith("save"):
            kind, channel, slot_number = "save", (r["slot"] or "autosave"), 0
        else:
            kind = "state"
            channel, slot_number = _state_identity(r["file_name"])
        key = f"{kind}|{r['emulator']}|{channel}|{slot_number}"
        conn.execute(
            sa.text(
                "UPDATE game_assets SET channel=:channel, slot_number=:slot_number, unit_key=:key, "
                "slot=CASE WHEN :kind='save' THEN :channel ELSE NULL END WHERE id=:id"
            ),
            {"channel": channel, "slot_number": slot_number, "key": key, "kind": kind, "id": r["id"]},
        )
        units.setdefault((r["user_id"], r["catalog_game_id"], key), []).append(r)

    # Two rows for one unit came from uploads under different file names; keep the newest.
    for members in units.values():
        if len(members) < 2:
            continue
        members.sort(key=lambda m: (m["updated_at"] or 0, m["id"]), reverse=True)
        for stale in members[1:]:
            conn.execute(sa.text("DELETE FROM game_assets WHERE id=:id"), {"id": stale["id"]})

    op.drop_constraint("unique_game_asset", "game_assets", type_="unique")
    op.create_unique_constraint(
        "unique_game_asset_unit", "game_assets", ["user_id", "catalog_game_id", "unit_key"]
    )


def downgrade() -> None:
    op.drop_constraint("unique_game_asset_unit", "game_assets", type_="unique")
    op.create_unique_constraint(
        "unique_game_asset",
        "game_assets",
        ["user_id", "catalog_game_id", "kind", "emulator", "file_name"],
    )
    op.drop_column("game_assets", "updated_by_device_id")
    op.drop_column("game_assets", "unit_key")
    op.drop_column("game_assets", "slot_number")
    op.drop_column("game_assets", "channel")
