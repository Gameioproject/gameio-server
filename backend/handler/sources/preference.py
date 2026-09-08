"""Which of a game's sources to hand out when the caller did not pick one."""

from typing import Final

from models.game_source import GameHostKind, GameSource

# Earlier is better; anything else sorts after these.
_REGION_ORDER: Final = ("USA", "World", "Europe", "Europe, Australia", "Japan")


def source_rank(source: GameSource) -> tuple[int, int, int, int]:
    """Direct hosts before debrid-resolved torrents, smaller torrents before larger ones
    (debrid services cap a torrent by its total size), then by region, then oldest first."""
    region = source.region or ""
    region_rank = next(
        (i for i, name in enumerate(_REGION_ORDER) if region.startswith(name)),
        len(_REGION_ORDER),
    )
    host = source.host
    torrent_size = 0
    if host.kind == GameHostKind.TORRENT:
        torrent_size = int((host.last_index_stats or {}).get("torrent_size") or 2**62)
    return (
        1 if host.kind == GameHostKind.TORRENT else 0,
        torrent_size,
        region_rank,
        source.id,
    )


def preferred_sources(sources: list[GameSource]) -> list[GameSource]:
    return sorted(sources, key=source_rank)
