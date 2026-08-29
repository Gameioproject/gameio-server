import pytest

from handler.sources.platforms import (
    platform_from_extension,
    platform_from_files,
    platform_from_folder,
    platform_from_text,
)


def test_platform_from_folder():
    assert platform_from_folder("n64") == "n64"
    assert platform_from_folder("Nintendo 64") == "n64"
    assert platform_from_folder("PlayStation") == "psx"
    assert platform_from_folder("misc") is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Redump - Sony - PS2 - NTSC-U (2016-September) Part 2", "ps2"),
        ("RedumpSonyPS2NTSCUPart2", "ps2"),
        ("ps1-rip-chd-ck", "psx"),
        ("roms-bestset-nintendo-64", "n64"),
        ("Game Boy Advance complete set", "gba"),
        ("Super Famicom collection", "snes"),
        ("Xbox 360 games", "xbox360"),
        ("Wii U games", None),
        ("Some random item", None),
    ],
)
def test_platform_from_text(text: str, expected: str | None):
    assert platform_from_text(text) == expected


def test_platform_from_text_uses_the_first_hint_it_finds():
    assert platform_from_text(None, "", "PlayStation 2") == "ps2"


def test_platform_from_extension():
    assert platform_from_extension("Game (USA).z64") == "n64"
    assert platform_from_extension("Game (USA).n64.zip") == "n64"
    assert platform_from_extension("Game (USA).gba.7z") == "gba"
    assert platform_from_extension("Game (USA).chd") is None


def test_platform_from_files_needs_a_clear_majority():
    assert platform_from_files(["a.z64", "b.n64.zip", "c.v64", "d.chd"]) == "n64"
    assert platform_from_files(["a.z64", "b.gba"]) is None
    assert platform_from_files(["a.chd", "b.iso"]) is None
