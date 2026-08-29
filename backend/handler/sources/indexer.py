"""Match a host's file listing against the catalog and record the hits as sources."""

import re
from dataclasses import dataclass, field
from typing import Final

from adapters.services.internet_archive import IAFile
from handler.database import db_catalog_handler, db_game_source_handler
from handler.database.game_source_handler import GameSourceInput
from handler.sources.matcher import (
    TitleMatcher,
    normalize_title,
    normalize_title_tokens,
)
from handler.sources.platforms import platform_from_extension, platform_from_folder
from models.base import compute_file_extension
from models.game_source import GameHost

# Files the Internet Archive adds to every item, never games.
IA_METADATA_SUFFIXES: Final = ("_meta.xml", "_files.xml", "_meta.sqlite", ".torrent")
# Sidecars that sit next to games in most dumps.
NON_GAME_EXTENSIONS: Final = frozenset(
    {
        "xml",
        "sqlite",
        "torrent",
        "txt",
        "nfo",
        "md",
        "pdf",
        "html",
        "htm",
        "json",
        "csv",
        "dat",
        "sfv",
        "md5",
        "sha1",
        "log",
        "ini",
        "url",
        "db",
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "webp",
        "mp4",
        "mkv",
        "avi",
        "mp3",
        "srt",
        "doc",
        "docx",
        "xls",
        "xlsx",
        "diz",
    }
)
UNMATCHED_SAMPLE_SIZE: Final = 25

__all__ = [
    "IndexStats",
    "index_host_files",
    "is_game_file",
    "normalize_title",
    "normalize_title_tokens",
    "platform_from_folder",
]


@dataclass
class IndexStats:
    files_seen: int = 0
    files_skipped: int = 0
    matched: int = 0
    unmatched: int = 0
    created: int = 0
    updated: int = 0
    unmatched_sample: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "files_seen": self.files_seen,
            "files_skipped": self.files_skipped,
            "matched": self.matched,
            "unmatched": self.unmatched,
            "created": self.created,
            "updated": self.updated,
            "unmatched_sample": list(self.unmatched_sample),
        }


def is_game_file(file: IAFile) -> bool:
    if file["source"] != "original":
        return False
    name = file["name"].lower()
    if name.endswith(IA_METADATA_SUFFIXES):
        return False
    return compute_file_extension(name) not in NON_GAME_EXTENSIONS


_TAG_GROUP = re.compile(r"\(([^)]*)\)")
_REGIONS: Final = {
    "USA": "USA",
    "US": "USA",
    "Europe": "Europe",
    "EU": "Europe",
    "Japan": "Japan",
    "JP": "Japan",
    "World": "World",
    "Asia": "Asia",
    "Australia": "Australia",
    "Brazil": "Brazil",
    "Canada": "Canada",
    "China": "China",
    "France": "France",
    "Germany": "Germany",
    "Italy": "Italy",
    "Korea": "Korea",
    "Netherlands": "Netherlands",
    "Russia": "Russia",
    "Spain": "Spain",
    "Sweden": "Sweden",
    "Taiwan": "Taiwan",
    "UK": "UK",
}


def _region(filename: str) -> str | None:
    """No-Intro region tags: "Game (Japan, USA) (En,Ja)" -> "Japan, USA"."""
    regions: list[str] = []
    for group in _TAG_GROUP.findall(filename):
        for tag in group.split(","):
            region = _REGIONS.get(tag.strip())
            if region and region not in regions:
                regions.append(region)
    return ", ".join(regions) if regions else None


def index_host_files(
    host: GameHost, files: list[IAFile], default_platform: str | None = None
) -> IndexStats:
    """Turn a host's file list into sources for every file whose title is in the catalog.

    Args:
        default_platform: Fallback when neither the host nor a folder names the system.
    """
    stats = IndexStats()
    matchers: dict[str, TitleMatcher] = {}
    pending: list[GameSourceInput] = []

    for file in files:
        stats.files_seen += 1
        if not is_game_file(file):
            stats.files_skipped += 1
            continue

        segments = file["name"].split("/")
        filename = segments[-1]
        platform_slug = (
            host.platform_slug or default_platform or platform_from_extension(filename)
        )
        if len(segments) > 1:
            platform_slug = platform_from_folder(segments[0]) or platform_slug
        if not platform_slug:
            stats.unmatched += 1
            _sample(stats, file["name"])
            continue

        if platform_slug not in matchers:
            matchers[platform_slug] = _matcher(platform_slug)
        game_id = matchers[platform_slug].match(filename)
        if game_id is None:
            stats.unmatched += 1
            _sample(stats, file["name"])
            continue

        stats.matched += 1
        pending.append(
            {
                "catalog_game_id": game_id,
                "path": file["name"],
                "filename": filename,
                "platform_slug": platform_slug,
                "size": file["size"],
                "md5": file["md5"],
                "sha1": file["sha1"],
                "region": _region(filename),
            }
        )

    if pending:
        stats.created, stats.updated = db_game_source_handler.upsert_sources(
            host.id, pending
        )
    return stats


def _matcher(platform_slug: str) -> TitleMatcher:
    games = db_catalog_handler.get_games_of_platform(platform_slug)
    return TitleMatcher((game.id, game.name) for game in games)


def _sample(stats: IndexStats, name: str) -> None:
    if len(stats.unmatched_sample) < UNMATCHED_SAMPLE_SIZE:
        stats.unmatched_sample.append(name)
