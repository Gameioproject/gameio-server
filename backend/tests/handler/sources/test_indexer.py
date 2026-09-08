import pytest

from adapters.services.internet_archive import IAFile
from handler.database import db_catalog_handler, db_game_source_handler
from handler.database.catalog_handler import CatalogGameInput
from handler.sources.indexer import index_host_files, is_game_file
from models.game_source import GameHost, GameHostKind


def _game(igdb_id: int, name: str, platform_slug: str) -> CatalogGameInput:
    return {
        "igdb_id": igdb_id,
        "name": name,
        "slug": None,
        "summary": None,
        "release_year": None,
        "first_release_date": None,
        "cover_image_id": None,
        "screenshot_image_ids": [],
        "genres": [],
        "platform_slugs": [platform_slug],
        "rating": None,
        "rating_count": 0,
        "youtube_video_id": None,
        "igdb_url": None,
        "source_updated_at": None,
    }


def _file(name: str, source: str = "original", size: int | None = 1024) -> IAFile:
    return {"name": name, "source": source, "size": size, "md5": "m" * 32, "sha1": None}


@pytest.fixture
def games():
    db_catalog_handler.upsert_games(
        [
            _game(1074, "Super Mario 64", "n64"),
            _game(1029, "The Legend of Zelda: Ocarina of Time", "n64"),
            _game(1638, "GoldenEye 007", "n64"),
            _game(6080, "PaRappa the Rapper", "psx"),
        ]
    )


@pytest.fixture
def host() -> GameHost:
    return db_game_source_handler.add_host(
        name="My item",
        kind=GameHostKind.INTERNET_ARCHIVE,
        base="my-item",
        platform_slug="n64",
    )


def test_is_game_file_skips_archive_metadata_and_derivatives():
    assert is_game_file(_file("n64/Super Mario 64 (USA).z64"))
    assert not is_game_file(_file("my-item_meta.xml"))
    assert not is_game_file(_file("my-item_files.xml"))
    assert not is_game_file(_file("my-item_archive.torrent"))
    assert not is_game_file(_file("README.txt"))
    assert not is_game_file(_file("covers/Super Mario 64.png"))
    assert is_game_file(_file("Super Mario 64 (USA).7z"))
    assert not is_game_file(_file("n64/Super Mario 64 (USA).z64", source="derivative"))


def test_index_host_files_records_matches(games, host: GameHost):
    files = [
        _file("my-item_meta.xml"),
        _file("Super Mario 64 (USA).z64", size=8388608),
        _file("n64/Legend of Zelda, The - Ocarina of Time (USA).z64"),
        _file("007 - GoldenEye (USA).n64.zip"),
        _file("PlayStation/PaRappa the Rapper (USA).chd"),
        _file("n64/Unknown Game (USA).z64"),
        _file("Atari 2600/Pitfall.a26"),
    ]
    stats = index_host_files(host, files)

    assert stats.files_seen == 7
    assert stats.files_skipped == 1
    assert stats.matched == 4
    assert stats.unmatched == 2
    assert stats.created == 4
    assert stats.updated == 0
    assert stats.unmatched_sample == [
        "n64/Unknown Game (USA).z64",
        "Atari 2600/Pitfall.a26",
    ]

    by_igdb = {
        s.game.igdb_id: s
        for match in [
            db_catalog_handler.get_game_by_igdb_id(i) for i in (1074, 1029, 6080)
        ]
        if match
        for s in match["sources"]
    }
    mario = by_igdb[1074]
    assert mario.path == "Super Mario 64 (USA).z64"
    assert mario.platform_slug == "n64"
    assert mario.size == 8388608
    assert mario.region == "USA"
    assert (
        mario.url
        == "https://archive.org/download/my-item/Super%20Mario%2064%20%28USA%29.z64"
    )
    assert by_igdb[6080].platform_slug == "psx"

    # Re-indexing updates in place instead of duplicating.
    again = index_host_files(host, files)
    assert (again.created, again.updated) == (0, 4)
    assert len(db_game_source_handler.get_sources_for_game(mario.catalog_game_id)) == 1


def test_index_host_files_without_platform_hint(games):
    host = db_game_source_handler.add_host(
        name="Flat", kind=GameHostKind.INTERNET_ARCHIVE, base="flat"
    )
    # A .z64 can only be Nintendo 64; a .chd could be several systems.
    stats = index_host_files(
        host,
        [_file("Super Mario 64 (USA).z64"), _file("PaRappa the Rapper (USA).chd")],
    )
    assert stats.matched == 1
    assert stats.unmatched == 1

    detected = index_host_files(
        host, [_file("PaRappa the Rapper (USA).chd")], default_platform="psx"
    )
    assert detected.matched == 1


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Redump/Sony - PlayStation 2/Shadow of the Colossus (USA).zip", True),
        ("Redump/Sony - PlayStation 2/Shadow of the Colossus (USA) (Demo).zip", False),
        ("Ico (Japan) (Taikenban).zip", False),
        ("Game (USA) (Beta 2).zip", False),
        ("Game (USA) (Proto).zip", False),
        ("Demolition Racer (USA).zip", True),
        ("007 - Agent Under Fire (USA) (Widescreen + 60FPS Driving) (v1.0) (Souzooka).chd", False),
        ("007 - Agent Under Fire (USA).chd.729c02d5.partial", False),
        ("007 - Agent Under Fire (USA).chd", True),
        ("Game (Europe) (En,Fr,De).zip", True),
    ],
)
def test_is_game_file_skips_discs_that_are_not_the_game(name: str, expected: bool):
    assert is_game_file(_file(name)) is expected
