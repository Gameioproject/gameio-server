from types import SimpleNamespace

import pytest

from handler.sources import resolver
from models.game_source import GameHost, GameHostKind, GameSource


def _torrent_source(file_index: int | None) -> GameSource:
    host = GameHost(name="minerva-ps2", kind=GameHostKind.TORRENT, base="x", info_hash="a" * 40)
    return GameSource(host=host, path="Redump/Sony - PlayStation 2/Game (USA).zip", file_index=file_index)


def test_torrent_source_magnet_selects_only_its_file():
    assert _torrent_source(12147).magnet == "magnet:?xt=urn:btih:" + "a" * 40 + "&dn=minerva-ps2&so=12147"
    assert _torrent_source(None).magnet == "magnet:?xt=urn:btih:" + "a" * 40 + "&dn=minerva-ps2"


def test_http_source_has_no_magnet():
    host = GameHost(name="files", kind=GameHostKind.HTTP, base="https://files.example.com")
    assert GameSource(host=host, path="Game.zip").magnet is None


async def test_resolver_hands_the_select_only_magnet_to_debrid(monkeypatch):
    seen = {}

    async def fake_resolve(info_hash, magnet, path):
        seen.update(info_hash=info_hash, magnet=magnet, path=path)
        return "https://dl.example/Game.zip"

    monkeypatch.setattr(resolver, "resolve_torrent_file", fake_resolve)
    assert await resolver.resolve_source_url(_torrent_source(7)) == "https://dl.example/Game.zip"
    assert seen["magnet"].endswith("&so=7")
    assert seen["path"] == "Redump/Sony - PlayStation 2/Game (USA).zip"


async def test_resolver_passes_direct_hosts_through():
    host = GameHost(name="ia", kind=GameHostKind.INTERNET_ARCHIVE, base="item")
    source = GameSource(host=host, path="Game.zip")
    assert await resolver.resolve_source_url(source) == "https://archive.org/download/item/Game.zip"


async def test_resolver_refuses_an_unindexed_torrent_host():
    host = GameHost(name="t", kind=GameHostKind.TORRENT, base="x", info_hash=None)
    with pytest.raises(ValueError):
        await resolver.resolve_source_url(GameSource(host=host, path="a.zip"))
