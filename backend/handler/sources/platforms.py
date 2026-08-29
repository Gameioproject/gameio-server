"""Guess which platform a host, folder or file belongs to."""

import re
from collections import Counter
from collections.abc import Iterable
from typing import Final

from handler.metadata.platforms import IGDB_PLATFORM_LIST
from handler.metadata.platforms import UniversalPlatformSlug as UPS
from models.base import compute_file_extension

_PLATFORM_BY_NAME: Final[dict[str, str]] = {
    platform["name"].lower(): slug.value
    for slug, platform in IGDB_PLATFORM_LIST.items()
}
_PLATFORM_SLUGS: Final[frozenset[str]] = frozenset(slug.value for slug in UPS)

# Most specific first: "PlayStation 2" must win over "PlayStation".
_TEXT_HINTS: Final[tuple[tuple[re.Pattern[str], str], ...]] = tuple(
    (re.compile(pattern), slug)
    for pattern, slug in (
        (r"playstation[ -]?2\b|\bps[ -]?2\b", "ps2"),
        (r"playstation[ -]?3\b|\bps[ -]?3\b", "ps3"),
        (r"playstation portable|\bpsp\b", "psp"),
        (r"playstation([ -]?1)?\b|\bps[ -]?1\b|\bps[ -]?x\b|\bpsone\b", "psx"),
        (r"nintendo[ -]?64\b|\bn[ -]?64\b", "n64"),
        (r"game[ -]?boy[ -]?advance|\bgba\b", "gba"),
        (r"game[ -]?boy[ -]?colou?r|\bgbc\b", "gbc"),
        (r"game[ -]?boy\b|\bgb\b", "gb"),
        (r"nintendo[ -]?ds\b|\bnds\b", "nds"),
        (r"super[ -]?nintendo|super[ -]?famicom|\bsnes\b|\bsfc\b", "snes"),
        (r"nintendo entertainment system|\bnes\b|\bfamicom\b", "nes"),
        (r"game[ -]?cube|\bngc\b|\bgcn\b", "ngc"),
        (r"xbox[ -]?360\b", "xbox360"),
        (r"\bxbox\b", "xbox"),
        (r"\bwii\b(?![ -]?u)", "wii"),
        (r"dreamcast|\bdc\b", "dc"),
        (r"\bsaturn\b", "saturn"),
        (r"sega[ -]?cd|mega[ -]?cd", "segacd"),
        (r"\b32x\b", "sega32"),
        (r"\bgenesis\b|mega[ -]?drive", "genesis"),
        (r"game[ -]?gear", "gamegear"),
        (r"master[ -]?system", "sms"),
        (r"turbo[ -]?grafx|pc[ -]?engine|\btg[ -]?16\b", "tg16"),
        (r"neo[ -]?geo", "neogeoaes"),
        (r"atari[ -]?2600", "atari2600"),
    )
)

# Extensions that belong to a single system.
_EXTENSION_HINTS: Final[dict[str, str]] = {
    "z64": "n64",
    "n64": "n64",
    "v64": "n64",
    "gba": "gba",
    "gbc": "gbc",
    "gb": "gb",
    "nds": "nds",
    "sfc": "snes",
    "smc": "snes",
    "nes": "nes",
    "fds": "nes",
    "md": "genesis",
    "gen": "genesis",
    "smd": "genesis",
    "gg": "gamegear",
    "sms": "sms",
    "pce": "tg16",
    "a26": "atari2600",
    "32x": "sega32",
    "gdi": "dc",
    "cdi": "dc",
    "cso": "psp",
    "gcm": "ngc",
    "gcz": "ngc",
    "wbfs": "wii",
    "wad": "wii",
    "xex": "xbox360",
}

_CAMEL_BOUNDARY = re.compile(
    r"(?<=[a-z])(?=[A-Z])|(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])"
)
_TAGS = re.compile(r"<[^>]+>")


def platform_from_folder(folder: str) -> str | None:
    """Resolve a folder name to a universal platform slug, by slug or IGDB name."""
    candidate = folder.strip().lower()
    if candidate in _PLATFORM_SLUGS:
        return candidate
    return _PLATFORM_BY_NAME.get(candidate)


def platform_from_text(*texts: str | None) -> str | None:
    """Find a system name in free text such as an item title, its tags or its identifier."""
    parts = []
    for text in texts:
        if not text:
            continue
        text = _TAGS.sub(" ", text)
        parts.append(text)
        parts.append(_CAMEL_BOUNDARY.sub(" ", text))
    haystack = " ".join(parts).lower()
    for pattern, slug in _TEXT_HINTS:
        if pattern.search(haystack):
            return slug
    return None


def platform_from_extension(file_name: str) -> str | None:
    """Systems with their own ROM extension: "Game.z64" can only be Nintendo 64."""
    name = file_name.lower()
    for archive in (".zip", ".7z", ".rar"):
        if name.endswith(archive):
            name = name[: -len(archive)]
    return _EXTENSION_HINTS.get(compute_file_extension(name))


def platform_from_files(file_names: Iterable[str], share: float = 0.8) -> str | None:
    """The system most files point at by extension, when they mostly agree."""
    votes = Counter(slug for slug in map(platform_from_extension, file_names) if slug)
    if not votes:
        return None
    slug, count = votes.most_common(1)[0]
    return slug if count >= share * sum(votes.values()) else None
