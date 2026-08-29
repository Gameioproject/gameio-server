"""Import the retro games catalog from a `retroaddon` SQLite database.

Usage (from `backend/`):
    uv run python tools/import_catalog.py /path/to/games.db [--platform psx,n64]

The source schema is the one written by retroaddon's `fetch-igdb.js`: a `games`
table keyed by IGDB id plus `game_platforms(game_id, platform_id)` holding IGDB
platform ids. Platforms are mapped to RomM's universal slugs; games on platforms
RomM does not know are skipped.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from handler.database import db_catalog_handler  # noqa: E402
from handler.database.catalog_handler import CatalogGameInput  # noqa: E402
from handler.metadata.platforms import IGDB_PLATFORM_LIST  # noqa: E402
from logger.logger import log  # noqa: E402

IMPORT_CHUNK_SIZE = 2000

IGDB_ID_TO_SLUG: dict[int, str] = {
    platform["id"]: slug.value for slug, platform in IGDB_PLATFORM_LIST.items()
}


def _load_json_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [str(v) for v in value] if isinstance(value, list) else []


def _release_year(row: sqlite3.Row) -> int | None:
    if row["year"]:
        return int(row["year"])
    if row["released"]:
        return datetime.fromtimestamp(int(row["released"]), tz=timezone.utc).year
    return None


def read_catalog(
    db_path: Path, only_slugs: set[str] | None = None
) -> tuple[list[CatalogGameInput], int]:
    """Return the games to import and how many were skipped for unknown platforms."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    platforms_by_game: dict[int, set[str]] = {}
    unknown_platform_ids: set[int] = set()
    for game_id, platform_id in conn.execute(
        "SELECT game_id, platform_id FROM game_platforms"
    ):
        slug = IGDB_ID_TO_SLUG.get(platform_id)
        if slug is None:
            unknown_platform_ids.add(platform_id)
            continue
        if only_slugs and slug not in only_slugs:
            continue
        platforms_by_game.setdefault(game_id, set()).add(slug)

    if unknown_platform_ids:
        log.warning(
            f"Skipping IGDB platform ids RomM does not know: {sorted(unknown_platform_ids)}"
        )

    games: list[CatalogGameInput] = []
    skipped = 0
    for row in conn.execute("SELECT * FROM games"):
        slugs = platforms_by_game.get(row["id"])
        if not slugs:
            skipped += 1
            continue
        games.append(
            {
                "igdb_id": int(row["id"]),
                "name": row["name"],
                "slug": row["slug"],
                "summary": row["summary"],
                "release_year": _release_year(row),
                "first_release_date": (
                    int(row["released"]) if row["released"] else None
                ),
                "cover_image_id": row["cover"],
                "screenshot_image_ids": _load_json_list(row["screenshots"]),
                "genres": _load_json_list(row["genres"]),
                "platform_slugs": sorted(slugs),
                "rating": float(row["rating"]) if row["rating"] is not None else None,
                "rating_count": int(row["rating_count"] or 0),
                "youtube_video_id": row["yt_id"],
                "igdb_url": row["url"],
                "source_updated_at": (
                    int(row["updated_at"]) if row["updated_at"] else None
                ),
            }
        )
    conn.close()
    return games, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("db_path", type=Path, help="Path to retroaddon's games.db")
    parser.add_argument(
        "--platform",
        help="Comma-separated RomM platform slugs to import (default: all)",
    )
    args = parser.parse_args()

    if not args.db_path.is_file():
        parser.error(f"{args.db_path} is not a file")

    only_slugs = (
        {s.strip() for s in args.platform.split(",") if s.strip()}
        if args.platform
        else None
    )
    games, skipped = read_catalog(args.db_path, only_slugs)
    log.info(f"Read {len(games)} games from {args.db_path} ({skipped} skipped)")

    written = 0
    for start in range(0, len(games), IMPORT_CHUNK_SIZE):
        written += db_catalog_handler.upsert_games(
            games[start : start + IMPORT_CHUNK_SIZE]
        )
        log.info(f"Imported {written}/{len(games)}")
    log.info(f"Catalog import complete: {written} games written")


if __name__ == "__main__":
    main()
