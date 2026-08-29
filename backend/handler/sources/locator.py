"""Map a pasted direct link onto a host + relative path, creating the host if needed."""

from dataclasses import dataclass
from urllib.parse import unquote, urlsplit

from handler.database import db_game_source_handler
from models.game_source import GameHost, GameHostKind

IA_DOWNLOAD_HOSTS = frozenset({"archive.org", "www.archive.org"})
IA_DOWNLOAD_PREFIX = "/download/"


@dataclass(frozen=True)
class Locator:
    kind: GameHostKind
    base: str
    path: str
    name: str


def parse_direct_link(url: str) -> Locator:
    """Split a direct link into the host it belongs to and the path on that host."""
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError("A direct link must start with http:// or https://")
    path = unquote(parts.path)
    if parts.netloc.lower() in IA_DOWNLOAD_HOSTS and path.startswith(
        IA_DOWNLOAD_PREFIX
    ):
        identifier, _, rest = path[len(IA_DOWNLOAD_PREFIX) :].partition("/")
        if not identifier or not rest:
            raise ValueError("An Internet Archive link needs an item and a file")
        return Locator(GameHostKind.INTERNET_ARCHIVE, identifier, rest, identifier)
    rest = path.lstrip("/")
    if not rest:
        raise ValueError("The link does not point at a file")
    origin = f"{parts.scheme}://{parts.netloc}"
    return Locator(GameHostKind.HTTP, origin, rest, parts.netloc)


def find_or_create_host(locator: Locator, platform_slug: str | None) -> GameHost:
    host = db_game_source_handler.get_host_by_base(locator.kind, locator.base)
    if host is not None:
        return host
    return db_game_source_handler.add_host(
        name=locator.name,
        kind=locator.kind,
        base=locator.base,
        platform_slug=platform_slug,
    )
