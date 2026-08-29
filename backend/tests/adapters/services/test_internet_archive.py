import pytest

from adapters.services.internet_archive import parse_item_identifier


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("roms-bestset-nintendo-64", "roms-bestset-nintendo-64"),
        ("  ps1-rip-chd-ck ", "ps1-rip-chd-ck"),
        ("https://archive.org/details/ps1-rip-chd-ck", "ps1-rip-chd-ck"),
        (
            "https://archive.org/download/RedumpSonyPS2NTSCUPart2",
            "RedumpSonyPS2NTSCUPart2",
        ),
        (
            "https://archive.org/download/RedumpSonyPS2NTSCUPart2/MLB%2006.7z",
            "RedumpSonyPS2NTSCUPart2",
        ),
    ],
)
def test_parse_item_identifier(value: str, expected: str):
    assert parse_item_identifier(value) == expected


@pytest.mark.parametrize(
    "value",
    ["", "https://example.com/details/x", "https://archive.org/", "bad id/with slash"],
)
def test_parse_item_identifier_rejects(value: str):
    with pytest.raises(ValueError):
        parse_item_identifier(value)
