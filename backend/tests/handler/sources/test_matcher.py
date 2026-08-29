import pytest

from handler.sources.matcher import (
    TitleMatcher,
    clean_title,
    normalize_title,
    normalize_title_tokens,
    title_variants,
)


@pytest.mark.parametrize(
    ("file_name", "cleaned"),
    [
        ("Armorines - Project S.W.A.R.M.chd", "armorines project s w a r m"),
        ("Bio F.R.E.A.K.S.chd", "bio f r e a k s"),
        ("Game (USA).n64.zip", "game"),
        ("Legend of Zelda, The - Ocarina (USA).z64", "the legend of zelda ocarina"),
        ("Pokémon Snap (USA).7z", "pokemon snap"),
        ("Sonic & Knuckles (World).md", "sonic and knuckles"),
    ],
)
def test_clean_title(file_name: str, cleaned: str):
    assert clean_title(file_name) == cleaned


def test_normalize_title_keys():
    assert normalize_title("Super Mario 64 (USA) (Rev 1).z64") == "supermario64"
    assert normalize_title_tokens("007 - GoldenEye.n64.zip") == normalize_title_tokens(
        "GoldenEye 007"
    )


def test_title_variants_cover_articles_brands_and_numerals():
    variants = title_variants(clean_title("Disney's The Lion King II (USA).7z"))
    assert variants[0] == "disneys the lion king ii"
    assert "the lion king 2" in variants
    assert "lion king 2" in variants


@pytest.fixture
def matcher() -> TitleMatcher:
    return TitleMatcher(
        [
            (1, "Crash Bandicoot"),
            (2, "Crash Bandicoot: Warped"),
            (3, "Disney's Aladdin in Nasira's Revenge"),
            (4, "The Adventures of Lomax"),
            (5, "James Bond 007: Tomorrow Never Dies"),
            (6, "AI Shogi"),
            (7, "Cleopatra Fortune"),
            (8, "Viewtiful Joe 2"),
            (9, "NBA 08"),
            (10, "SoulCalibur III"),
            (11, "Final Fantasy VII"),
            (12, "Samurai Warriors 2"),
            (13, "Dinosaurs"),
        ]
    )


@pytest.mark.parametrize(
    ("file_name", "expected"),
    [
        ("Crash Bandicoot (USA).chd", 1),
        ("Crash Bandicoot 1.chd", 1),
        ("Crash Bandicoot 3 - Warped (USA).chd", 2),
        ("Aladdin in Nasira's Revenge.chd", 3),
        ("Adventures of Lomax.chd", 4),
        ("007 - Tomorrow Never Dies.chd", 5),
        ("AI Shougi.chd", 6),
        ("Cleopatras Fortune.chd", 7),
        ("Final Fantasy 7 (USA) (Disc 1).chd", 11),
        # Guarded fuzzy: numbers must agree and nothing else may be as close.
        ("Viewtiful Joe (USA).7z", None),
        ("NBA 06 (USA).7z", None),
        ("Soulcalibur II (USA).7z", None),
        ("Samurai Warriors 2 - Empires (USA).7z", None),
        ("Dinosaur.chd", None),
        ("Unknown Game.chd", None),
    ],
)
def test_matcher(matcher: TitleMatcher, file_name: str, expected: int | None):
    assert matcher.match(file_name) == expected


def test_matcher_drops_keys_two_games_share():
    matcher = TitleMatcher([(1, "Mega Man X"), (2, "Mega Man 10")])
    assert matcher.match("Mega Man X (USA).zip") == 1
    assert matcher.match("Mega Man 10 (USA).zip") == 2
    ambiguous = TitleMatcher([(1, "The Game"), (2, "Game")])
    assert ambiguous.match("Game (USA).zip") == 2
    assert ambiguous.match("The Game (USA).zip") == 1
