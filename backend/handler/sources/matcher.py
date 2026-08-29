"""Match archive file names to catalog titles.

Titles are compared through a small ladder: exact normalized name, then
spelling variants both sides can agree on (articles, brand prefixes, roman
numerals, "Game 1"), then a guarded fuzzy pass for typos and romanization.
"""

import difflib
import re
import unicodedata
from collections.abc import Iterable
from typing import Final

from models.base import compute_file_name_no_tags

FUZZY_MIN_RATIO: Final = 0.93
FUZZY_SURE_RATIO: Final = 0.96
FUZZY_MIN_GAP: Final = 0.02
# A near-identical title keeps its first letter and roughly its length.
FUZZY_LENGTH_SLACK: Final = 0.2

_NON_ALNUM = re.compile(r"[^a-z0-9]+")
# No-Intro style "Zelda, The - Ocarina" puts the article before the subtitle.
_MOVED_ARTICLE = re.compile(r"^(.*?), (the|a|an)\b(.*)$", re.IGNORECASE)
_INNER_EXTENSION = re.compile(r"\.([a-z0-9]{1,4})$", re.IGNORECASE)
_NUMBER = re.compile(r"\d+")

# Extensions archives keep inside the name: "Game (USA).n64.zip".
ROM_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {
        "z64",
        "n64",
        "v64",
        "nes",
        "fds",
        "sfc",
        "smc",
        "gba",
        "gb",
        "gbc",
        "nds",
        "dsi",
        "iso",
        "bin",
        "cue",
        "chd",
        "pbp",
        "cso",
        "img",
        "mdf",
        "md",
        "gen",
        "smd",
        "sms",
        "gg",
        "pce",
        "32x",
        "ngp",
        "ngc",
        "ws",
        "wsc",
        "a26",
        "a78",
        "rom",
        "gcm",
        "gcz",
        "rvz",
        "wbfs",
        "wad",
        "cdi",
        "gdi",
        "ecm",
        "xex",
        "vb",
        "lnx",
        "col",
        "int",
        "sg",
        "zip",
        "7z",
        "rar",
    }
)

ARTICLES: Final = ("the", "a", "an")
# Licensor names dump groups put in front of a title and IGDB usually drops.
BRAND_PREFIXES: Final = (
    "disney pixar",
    "disneys",
    "disney",
    "nickelodeon",
    "nick jr",
    "cartoon network",
    "dreamworks",
    "shonen jumps",
    "tim burtons",
    "tom clancys",
    "sid meiers",
    "james bond",
    "marvels",
    "marvel",
    "espn",
    "mtv",
    "lego",
)
ROMAN_NUMERALS: Final = {
    "ii": "2",
    "iii": "3",
    "iv": "4",
    "v": "5",
    "vi": "6",
    "vii": "7",
    "viii": "8",
    "ix": "9",
    "x": "10",
    "xi": "11",
    "xii": "12",
    "xiii": "13",
    "xiv": "14",
    "xv": "15",
    "xvi": "16",
}
_LONG_VOWELS: Final = (("ou", "o"), ("uu", "u"))


def clean_title(name: str) -> str:
    """Lowercase words of a title, without extension, tags, accents or punctuation."""
    title = compute_file_name_no_tags(name)
    if (inner := _INNER_EXTENSION.search(title)) and inner.group(
        1
    ).lower() in ROM_EXTENSIONS:
        title = compute_file_name_no_tags(title[: inner.start()])
    if match := _MOVED_ARTICLE.match(title):
        title = f"{match.group(2)} {match.group(1)}{match.group(3)}"
    title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    title = title.lower().replace("&", " and ").replace("'", "")
    return " ".join(_NON_ALNUM.sub(" ", title).split())


def exact_key(cleaned: str) -> str:
    return cleaned.replace(" ", "")


def token_key(cleaned: str) -> str:
    """Order-insensitive key, so "007 - GoldenEye" still meets "GoldenEye 007"."""
    return "".join(sorted(cleaned.split()))


def normalize_title(name: str) -> str:
    """Collapse a title to a comparison key: "Zelda, The: Link's Awakening" == "the zelda links awakening"."""
    return exact_key(clean_title(name))


def normalize_title_tokens(name: str) -> str:
    return token_key(clean_title(name))


def _romanize(cleaned: str) -> str:
    return " ".join(ROMAN_NUMERALS.get(word, word) for word in cleaned.split())


def _drop_article(cleaned: str) -> str:
    first, _, rest = cleaned.partition(" ")
    return rest if first in ARTICLES and rest else cleaned


def _drop_brand(cleaned: str) -> str:
    for brand in BRAND_PREFIXES:
        if cleaned.startswith(brand + " "):
            return cleaned[len(brand) + 1 :]
    return cleaned


def _drop_trailing_one(cleaned: str) -> str:
    return cleaned[:-2] if cleaned.endswith(" 1") else cleaned


def _fold_long_vowels(cleaned: str) -> str:
    for long, short in _LONG_VOWELS:
        cleaned = cleaned.replace(long, short)
    return cleaned


_VARIANT_STEPS = (
    _romanize,
    _drop_article,
    _drop_brand,
    _drop_article,
    _drop_trailing_one,
    _fold_long_vowels,
)


def title_variants(cleaned: str) -> list[str]:
    """Spellings of one title, most faithful first, without duplicates."""
    variants = [cleaned]
    for step in _VARIANT_STEPS:
        for variant in list(variants):
            changed = step(variant)
            if changed and changed not in variants:
                variants.append(changed)
    return variants


def _without_inner_number(cleaned: str) -> list[str]:
    """ "Crash Bandicoot 3 - Warped" also reads as "Crash Bandicoot: Warped"."""
    words = cleaned.split()
    return [
        " ".join(words[:i] + words[i + 1 :])
        for i, word in enumerate(words[:-1])
        if word.isdigit() and i > 0
    ]


def _numbers(cleaned: str) -> list[str]:
    return sorted(_NUMBER.findall(_romanize(cleaned)))


class TitleMatcher:
    """Resolve file names to catalog game ids for one platform."""

    def __init__(self, titles: Iterable[tuple[int, str]]):
        self._ids: dict[str, int | None] = {}
        self._tiers: dict[str, int] = {}
        self._plain: dict[str, tuple[int, str]] = {}
        self._buckets: dict[str, list[str]] = {}
        for game_id, name in titles:
            cleaned = clean_title(name)
            if not cleaned:
                continue
            key = exact_key(cleaned)
            if key not in self._plain:
                self._plain[key] = (game_id, cleaned)
                self._buckets.setdefault(key[0], []).append(key)
            for tier, variant in enumerate(title_variants(cleaned)):
                self._insert(exact_key(variant), game_id, tier * 2)
                self._insert(token_key(variant), game_id, tier * 2 + 1)

    def _insert(self, key: str, game_id: int, tier: int) -> None:
        if key not in self._ids:
            self._ids[key] = game_id
            self._tiers[key] = tier
        elif self._ids[key] != game_id:
            if tier < self._tiers[key]:
                self._ids[key] = game_id
                self._tiers[key] = tier
            elif tier == self._tiers[key]:
                # Two games spell the same under this variant; neither may claim it.
                self._ids[key] = None

    def match(self, file_name: str) -> int | None:
        cleaned = clean_title(file_name)
        if not cleaned:
            return None
        variants = title_variants(cleaned)
        candidates = variants + [
            extra for variant in variants for extra in _without_inner_number(variant)
        ]
        for keyed in (exact_key, token_key):
            for candidate in candidates:
                if (game_id := self._ids.get(keyed(candidate))) is not None:
                    return game_id
        return self._fuzzy(cleaned)

    def _fuzzy(self, cleaned: str) -> int | None:
        """Accept a near-identical title only when numbers agree and nothing else is close."""
        key = exact_key(cleaned)
        slack = max(3, int(len(key) * FUZZY_LENGTH_SLACK))
        pool = [
            other
            for other in self._buckets.get(key[0], ())
            if abs(len(other) - len(key)) <= slack
        ]
        close = difflib.get_close_matches(key, pool, n=2, cutoff=FUZZY_MIN_RATIO - 0.05)
        if not close:
            return None
        ratio = difflib.SequenceMatcher(None, key, close[0]).ratio()
        if ratio < FUZZY_MIN_RATIO:
            return None
        if len(close) > 1:
            runner_up = difflib.SequenceMatcher(None, key, close[1]).ratio()
            if ratio - runner_up < FUZZY_MIN_GAP:
                return None
        game_id, candidate = self._plain[close[0]]
        if _numbers(cleaned) != _numbers(candidate):
            return None
        words, candidate_words = set(cleaned.split()), set(candidate.split())
        contained = words <= candidate_words or candidate_words <= words
        if ratio < FUZZY_SURE_RATIO and not contained:
            return None
        return game_id
