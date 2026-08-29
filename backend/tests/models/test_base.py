import pytest

from models.base import compute_file_name_parts


@pytest.mark.parametrize(
    ("file_name", "no_tags", "no_ext", "extension"),
    [
        ("Sonic (USA) [!].md", "Sonic", "Sonic (USA) [!]", "md"),
        ("game.tar.gz", "game", "game", "tar.gz"),
        ("README", "README", "README", ""),
        (
            "Final Fantasy VII (Disc 1).bin",
            "Final Fantasy VII",
            "Final Fantasy VII (Disc 1)",
            "bin",
        ),
    ],
)
def test_compute_file_name_parts(file_name, no_tags, no_ext, extension):
    parts = compute_file_name_parts(file_name)

    assert parts.no_tags == no_tags
    assert parts.no_ext == no_ext
    assert parts.extension == extension
