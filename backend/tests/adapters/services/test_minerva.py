import hashlib

import pytest

from adapters.services.minerva import (
    parse_minerva_link,
    parse_torrent,
    torrent_files_as_listing,
)


@pytest.mark.parametrize(
    ("value", "directory", "torrent_url"),
    [
        (
            "https://minerva-archive.org/browse/./Redump/Sony%20-%20PlayStation%202/",
            "Redump/Sony - PlayStation 2/",
            None,
        ),
        (
            "https://minerva-archive.org/browse/Redump/Sony - PlayStation 2",
            "Redump/Sony - PlayStation 2/",
            None,
        ),
        (
            "https://minerva-archive.org/assets/Minerva_Myrient_v0.3/Minerva_Myrient%20-%20Redump%20-%20Sony%20-%20PlayStation%202.torrent",
            None,
            "https://minerva-archive.org/assets/Minerva_Myrient_v0.3/Minerva_Myrient%20-%20Redump%20-%20Sony%20-%20PlayStation%202.torrent",
        ),
    ],
)
def test_parse_minerva_link(value: str, directory: str | None, torrent_url: str | None):
    locator = parse_minerva_link(value)
    assert locator.directory == directory
    assert locator.torrent_url == torrent_url


def test_parse_minerva_link_canonical_directory():
    locator = parse_minerva_link("https://minerva-archive.org/browse/./Redump/Sony - PlayStation 2/")
    assert locator.canonical == (
        "https://minerva-archive.org/browse/./Redump/Sony%20-%20PlayStation%202/"
    )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "https://archive.org/details/x",
        "https://minerva-archive.org/browse/",
        "https://minerva-archive.org/rom?id=1",
        "https://minerva-archive.org/assets/notes.txt",
    ],
)
def test_parse_minerva_link_rejects(value: str):
    with pytest.raises(ValueError):
        parse_minerva_link(value)


def _bencode(value) -> bytes:
    if isinstance(value, int):
        return b"i%de" % value
    if isinstance(value, str):
        value = value.encode()
    if isinstance(value, bytes):
        return b"%d:" % len(value) + value
    if isinstance(value, list):
        return b"l" + b"".join(_bencode(v) for v in value) + b"e"
    if isinstance(value, dict):
        return b"d" + b"".join(_bencode(k) + _bencode(value[k]) for k in sorted(value)) + b"e"
    raise TypeError(type(value))


def _torrent() -> bytes:
    info = {
        "name": "Minerva_Myrient",
        "piece length": 16 * 1024 * 1024,
        "pieces": b"\x00" * 20,
        "files": [
            {"length": 3996601059, "path": ["Redump", "Sony - PlayStation 2", "0 Story (Japan) (Disc 1).zip"]},
            {"length": 12, "path": ["Redump", "Sony - PlayStation 2", "readme.txt"]},
            {"length": 50, "path": ["Redump", "Sony - PlayStation", "Other (USA).zip"]},
        ],
    }
    return _bencode(
        {
            "announce": "udp://tracker.opentrackr.org:1337/announce",
            "announce-list": [["udp://tracker.opentrackr.org:1337/announce"], ["udp://open.stealth.si:80/announce"]],
            "info": info,
        }
    )


def test_parse_torrent_reads_files_and_hash():
    data = _torrent()
    torrent = parse_torrent(data)
    info_start = data.index(b"4:infod") + len("4:info")
    expected = hashlib.sha1(data[info_start:-1]).hexdigest()
    assert torrent.info_hash == expected
    assert torrent.name == "Minerva_Myrient"
    assert [f.path for f in torrent.files] == [
        "Redump/Sony - PlayStation 2/0 Story (Japan) (Disc 1).zip",
        "Redump/Sony - PlayStation 2/readme.txt",
        "Redump/Sony - PlayStation/Other (USA).zip",
    ]
    assert torrent.files[0].size == 3996601059
    assert torrent.trackers == [
        "udp://tracker.opentrackr.org:1337/announce",
        "udp://open.stealth.si:80/announce",
    ]
    assert torrent.magnet.startswith(f"magnet:?xt=urn:btih:{expected}&dn=Minerva_Myrient&tr=")


def test_torrent_files_as_listing_limits_to_directory():
    torrent = parse_torrent(_torrent())
    files = torrent_files_as_listing(torrent, "Redump/Sony - PlayStation 2/")
    assert [f["name"] for f in files] == [
        "Redump/Sony - PlayStation 2/0 Story (Japan) (Disc 1).zip",
        "Redump/Sony - PlayStation 2/readme.txt",
    ]
    assert files[0]["source"] == "original"
    assert files[0]["size"] == 3996601059
    assert files[0]["md5"] is None
    assert [f["index"] for f in files] == [0, 1]
    assert len(torrent_files_as_listing(torrent, None)) == 3


def test_parse_torrent_rejects_other_files():
    with pytest.raises(ValueError):
        parse_torrent(b"d3:fooi1ee")
