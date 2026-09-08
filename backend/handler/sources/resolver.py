"""The URL a client downloads a source from, whatever kind of host holds it."""

from adapters.services.debrid import resolve_torrent_file
from models.game_source import GameHostKind, GameSource


async def resolve_source_url(source: GameSource) -> str:
    host = source.host
    if host.kind != GameHostKind.TORRENT:
        return source.url
    if not host.info_hash:
        raise ValueError(f"{host.name} has not been indexed yet")
    return await resolve_torrent_file(host.info_hash, source.magnet or host.url_for(""), source.path)
