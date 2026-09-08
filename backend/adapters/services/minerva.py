"""Read-only client for the MiNERVA Archive (the Myrient mirror, distributed by torrent).

MiNERVA serves no file over HTTP: a directory is one torrent, and each file page carries
the file's path inside that torrent plus its hashes. The archive is therefore indexed
from the torrent file itself, which lists every path and size in one download.
"""

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Final
from urllib.parse import quote, unquote, urlsplit

from adapters.services.internet_archive import IAFile
from utils.context import ctx_httpx_client

MINERVA_ORIGIN: Final = "https://minerva-archive.org"
MINERVA_HOSTS: Final = frozenset({"minerva-archive.org", "www.minerva-archive.org"})
MINERVA_REQUEST_TIMEOUT: Final = 120
# The site answers a bare httpx user agent with its HTML too, but a browser one is
# what it is tuned for and what its rate limits expect.
_HEADERS: Final = {"User-Agent": "Mozilla/5.0 (compatible; Gameio catalog indexer)"}

_BROWSE_PREFIX: Final = "/browse/"
_ASSETS_PREFIX: Final = "/assets/"
_ROM_LINK = re.compile(r'href="/rom\?id=(\d+)"')
_ROM_JSON = re.compile(r"window\.rom\s*=\s*(\{.*?\});", re.DOTALL)
_INFO_HASH = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class MinervaLocator:
    """Where on MiNERVA a host points: a directory of the listing, or a torrent file."""

    directory: str | None
    torrent_url: str | None

    @property
    def canonical(self) -> str:
        if self.torrent_url:
            return self.torrent_url
        assert self.directory is not None
        return f"{MINERVA_ORIGIN}{_BROWSE_PREFIX}./{quote(self.directory)}"


def parse_minerva_link(value: str) -> MinervaLocator:
    """Accept a MiNERVA browse directory link or a .torrent link."""
    parts = urlsplit(value.strip())
    if parts.scheme not in ("http", "https") or parts.netloc.lower() not in MINERVA_HOSTS:
        raise ValueError("Not a minerva-archive.org link")
    path = unquote(parts.path)
    if path.startswith(_ASSETS_PREFIX) and path.lower().endswith(".torrent"):
        return MinervaLocator(directory=None, torrent_url=f"{MINERVA_ORIGIN}{quote(path)}")
    if path.startswith(_BROWSE_PREFIX):
        directory = path[len(_BROWSE_PREFIX) :]
        while directory.startswith("./") or directory.startswith("/"):
            directory = directory[2:] if directory.startswith("./") else directory[1:]
        directory = directory.strip("/")
        if not directory:
            raise ValueError("Point at a directory of the listing, not the root")
        return MinervaLocator(directory=f"{directory}/", torrent_url=None)
    raise ValueError("Expected a minerva-archive.org/browse/... directory or a .torrent link")


@dataclass(frozen=True)
class TorrentFile:
    path: str
    size: int


@dataclass(frozen=True)
class TorrentInfo:
    info_hash: str
    name: str
    files: list[TorrentFile]
    trackers: list[str]

    @property
    def magnet(self) -> str:
        link = f"magnet:?xt=urn:btih:{self.info_hash}&dn={quote(self.name)}"
        return link + "".join(f"&tr={quote(tracker, safe='')}" for tracker in self.trackers)


async def fetch_torrent_url(locator: MinervaLocator) -> str:
    """The torrent behind a locator: a directory's first file page names it."""
    if locator.torrent_url:
        return locator.torrent_url
    client = ctx_httpx_client.get()
    listing = await client.get(
        locator.canonical, headers=_HEADERS, timeout=MINERVA_REQUEST_TIMEOUT
    )
    listing.raise_for_status()
    match = _ROM_LINK.search(listing.text)
    if match is None:
        raise ValueError("The directory lists no files")
    page = await client.get(
        f"{MINERVA_ORIGIN}/rom?id={match.group(1)}",
        headers=_HEADERS,
        timeout=MINERVA_REQUEST_TIMEOUT,
    )
    page.raise_for_status()
    rom = _ROM_JSON.search(page.text)
    if rom is None:
        raise ValueError("The file page carries no torrent reference")
    torrents = json.loads(rom.group(1)).get("torrents")
    if not torrents:
        raise ValueError("The file page names no torrent")
    return f"{MINERVA_ORIGIN}{_ASSETS_PREFIX}{quote(str(torrents))}"


async def fetch_torrent(url: str) -> TorrentInfo:
    client = ctx_httpx_client.get()
    response = await client.get(url, headers=_HEADERS, timeout=MINERVA_REQUEST_TIMEOUT)
    response.raise_for_status()
    return parse_torrent(response.content)


def parse_torrent(data: bytes) -> TorrentInfo:
    """Decode a .torrent: its info hash, name, file paths with sizes, and trackers."""
    decoded, _ = _bdecode(data, 0)
    if not isinstance(decoded, dict) or b"info" not in decoded:
        raise ValueError("Not a torrent file")
    info = decoded[b"info"]
    name = info.get(b"name", b"").decode("utf-8", "replace")
    entries = info.get(b"files")
    if entries is None:
        files = [TorrentFile(name, int(info.get(b"length", 0)))]
    else:
        files = [
            TorrentFile(
                "/".join(part.decode("utf-8", "replace") for part in entry[b"path"]),
                int(entry[b"length"]),
            )
            for entry in entries
            if entry.get(b"path")
        ]
    trackers: list[str] = []
    announce = decoded.get(b"announce")
    if isinstance(announce, bytes):
        trackers.append(announce.decode("utf-8", "replace"))
    for tier in decoded.get(b"announce-list", []) or []:
        for tracker in tier:
            text = tracker.decode("utf-8", "replace")
            if text not in trackers:
                trackers.append(text)
    return TorrentInfo(
        info_hash=hashlib.sha1(_bencode(info)).hexdigest(),
        name=name,
        files=files,
        trackers=trackers[:8],
    )


def torrent_files_as_listing(
    info: TorrentInfo, directory: str | None
) -> list[IAFile]:
    """The torrent's files in the shape the indexer reads, limited to one directory."""
    return [
        {
            "name": file.path,
            "source": "original",
            "size": file.size,
            "md5": None,
            "sha1": None,
            "index": index,
        }
        for index, file in enumerate(info.files)
        if directory is None or file.path.startswith(directory)
    ]


def is_info_hash(value: str) -> bool:
    return bool(_INFO_HASH.match(value))


def _bdecode(data: bytes, index: int) -> tuple[object, int]:
    lead = data[index : index + 1]
    if lead == b"i":
        end = data.index(b"e", index)
        return int(data[index + 1 : end]), end + 1
    if lead == b"l":
        index += 1
        items: list[object] = []
        while data[index : index + 1] != b"e":
            value, index = _bdecode(data, index)
            items.append(value)
        return items, index + 1
    if lead == b"d":
        index += 1
        mapping: dict[bytes, object] = {}
        while data[index : index + 1] != b"e":
            key, index = _bdecode(data, index)
            value, index = _bdecode(data, index)
            mapping[key] = value  # type: ignore[index]
        return mapping, index + 1
    colon = data.index(b":", index)
    length = int(data[index:colon])
    start = colon + 1
    return data[start : start + length], start + length


def _bencode(value: object) -> bytes:
    if isinstance(value, bool):
        value = int(value)
    if isinstance(value, int):
        return b"i%de" % value
    if isinstance(value, bytes):
        return b"%d:" % len(value) + value
    if isinstance(value, str):
        return _bencode(value.encode("utf-8"))
    if isinstance(value, list):
        return b"l" + b"".join(_bencode(item) for item in value) + b"e"
    if isinstance(value, dict):
        return (
            b"d"
            + b"".join(_bencode(key) + _bencode(value[key]) for key in sorted(value))
            + b"e"
        )
    raise TypeError(f"Cannot bencode {type(value).__name__}")
