from types import SimpleNamespace

from handler.sources.preference import preferred_sources
from models.game_source import GameHostKind


def _source(id: int, kind: GameHostKind, region: str | None, torrent_size: int | None = None):
    stats = {"torrent_size": torrent_size} if torrent_size else None
    return SimpleNamespace(
        id=id, region=region, host=SimpleNamespace(kind=kind, last_index_stats=stats)
    )


def test_direct_hosts_then_region_then_age():
    sources = [
        _source(5, GameHostKind.TORRENT, "USA"),
        _source(4, GameHostKind.TORRENT, "Japan"),
        _source(3, GameHostKind.INTERNET_ARCHIVE, "Europe"),
        _source(2, GameHostKind.INTERNET_ARCHIVE, "USA"),
        _source(1, GameHostKind.HTTP, None),
    ]
    assert [s.id for s in preferred_sources(sources)] == [2, 3, 1, 5, 4]


def test_smaller_torrent_wins_over_region():
    sources = [
        _source(1, GameHostKind.TORRENT, "USA", torrent_size=17 * 2**40),
        _source(2, GameHostKind.TORRENT, "Europe", torrent_size=2 * 2**40),
        _source(3, GameHostKind.TORRENT, "USA"),
    ]
    assert [s.id for s in preferred_sources(sources)] == [2, 1, 3]
