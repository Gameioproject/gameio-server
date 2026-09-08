"""Turn a file inside a torrent into a direct download link through a debrid service.

The catalog never touches the swarm itself. A torrent-backed source is resolved on
demand: the torrent is handed to the debrid account, the one file is selected, and the
service's own link for it is what the client downloads.
"""

import asyncio
import hashlib
from typing import Any, Final

import httpx

from config import DEBRID_API_KEY, DEBRID_PROVIDER
from handler.redis_handler import async_cache
from logger.logger import log
from utils.context import ctx_httpx_client

REAL_DEBRID_API: Final = "https://api.real-debrid.com/rest/1.0"
DEBRID_TIMEOUT: Final = 60
# A torrent already on the service turns "downloaded" within a few polls; anything
# slower means the service is still fetching it and the client should retry later.
READY_POLL_SECONDS: Final = 2.0
READY_POLL_ATTEMPTS: Final = 8
LINK_CACHE_SECONDS: Final = 6 * 60 * 60
TORRENT_CACHE_SECONDS: Final = 7 * 24 * 60 * 60
_FAILED_STATUSES: Final = frozenset({"magnet_error", "error", "virus", "dead"})


# Real-Debrid numeric error codes that name the problem better than the HTTP status.
RD_TORRENT_TOO_BIG: Final = 29
RD_TOO_MANY_ACTIVE: Final = 21
RD_TRAFFIC_EXHAUSTED: Final = 23
RD_FAIR_USAGE: Final = 36


class DebridError(Exception):
    """A resolution that did not produce a link; `retry_later` says whether it might."""

    def __init__(
        self, message: str, *, retry_later: bool = False, too_big: bool = False
    ) -> None:
        super().__init__(message)
        self.retry_later = retry_later
        # The service refuses the torrent for its total size; no retry will help.
        self.too_big = too_big


def debrid_configured() -> bool:
    return bool(DEBRID_API_KEY) and DEBRID_PROVIDER == "realdebrid"


async def resolve_torrent_file(info_hash: str, magnet: str, path: str) -> str:
    """A direct link for `path` inside the torrent `info_hash`, through the debrid account."""
    if not DEBRID_API_KEY:
        raise DebridError("No debrid account is configured (set DEBRID_API_KEY)")
    if DEBRID_PROVIDER != "realdebrid":
        raise DebridError(f"Unsupported debrid provider {DEBRID_PROVIDER!r}")
    key = f"{info_hash}:{hashlib.sha1(path.encode('utf-8')).hexdigest()}"
    cached = await async_cache.get(f"debrid:link:{key}")
    if cached:
        return cached.decode() if isinstance(cached, bytes) else str(cached)

    client = _RealDebrid(ctx_httpx_client.get())
    torrent_id = await async_cache.get(f"debrid:torrent:{key}")
    torrent_id = torrent_id.decode() if isinstance(torrent_id, bytes) else torrent_id
    info = await client.info(torrent_id) if torrent_id else None
    if info is None:
        torrent_id = await client.add_magnet(magnet)
        info = await client.info(torrent_id)
        file_id = _file_id(info, path)
        await client.select_files(torrent_id, file_id)
        await async_cache.set(f"debrid:torrent:{key}", torrent_id, ex=TORRENT_CACHE_SECONDS)

    for _ in range(READY_POLL_ATTEMPTS):
        status = str(info.get("status", ""))
        if status == "downloaded":
            break
        if status in _FAILED_STATUSES:
            await async_cache.delete(f"debrid:torrent:{key}")
            raise DebridError(f"The debrid service rejected the torrent ({status})")
        await asyncio.sleep(READY_POLL_SECONDS)
        info = await client.info(torrent_id) or info
    else:
        raise DebridError(
            "The debrid service is still fetching this file; try again in a while",
            retry_later=True,
        )

    links = [str(link) for link in info.get("links", []) if link]
    if not links:
        raise DebridError("The debrid service produced no link for this file")
    direct = await client.unrestrict(links[0])
    await async_cache.set(f"debrid:link:{key}", direct, ex=LINK_CACHE_SECONDS)
    log.info(f"Resolved {path} through {DEBRID_PROVIDER}")
    return direct


def _file_id(info: dict[str, Any], path: str) -> int:
    wanted = path.strip("/")
    files = info.get("files") or []
    for entry in files:
        if str(entry.get("path", "")).strip("/") == wanted:
            return int(entry["id"])
    filename = wanted.rsplit("/", 1)[-1]
    for entry in files:
        if str(entry.get("path", "")).rsplit("/", 1)[-1] == filename:
            return int(entry["id"])
    raise DebridError(f"The torrent on the debrid service has no file {wanted}")


class _RealDebrid:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client
        self._headers = {"Authorization": f"Bearer {DEBRID_API_KEY}"}

    async def add_magnet(self, magnet: str) -> str:
        payload = await self._post("/torrents/addMagnet", {"magnet": magnet})
        torrent_id = payload.get("id")
        if not torrent_id:
            raise DebridError("The debrid service did not accept the torrent")
        return str(torrent_id)

    async def info(self, torrent_id: str) -> dict[str, Any] | None:
        response = await self._client.get(
            f"{REAL_DEBRID_API}/torrents/info/{torrent_id}",
            headers=self._headers,
            timeout=DEBRID_TIMEOUT,
        )
        if response.status_code == 404:
            return None
        self._raise_for(response)
        payload = response.json()
        return payload if isinstance(payload, dict) else None

    async def select_files(self, torrent_id: str, file_id: int) -> None:
        response = await self._client.post(
            f"{REAL_DEBRID_API}/torrents/selectFiles/{torrent_id}",
            data={"files": str(file_id)},
            headers=self._headers,
            timeout=DEBRID_TIMEOUT,
        )
        self._raise_for(response)

    async def unrestrict(self, link: str) -> str:
        payload = await self._post("/unrestrict/link", {"link": link})
        direct = payload.get("download")
        if not direct:
            raise DebridError("The debrid service returned no download link")
        return str(direct)

    async def _post(self, route: str, data: dict[str, str]) -> dict[str, Any]:
        response = await self._client.post(
            f"{REAL_DEBRID_API}{route}",
            data=data,
            headers=self._headers,
            timeout=DEBRID_TIMEOUT,
        )
        self._raise_for(response)
        payload = response.json()
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _raise_for(response: httpx.Response) -> None:
        if response.status_code < 400:
            return
        detail = ""
        code: int | None = None
        try:
            body = response.json()
            detail = str(body.get("error") or body)
            code = body.get("error_code") if isinstance(body, dict) else None
        except ValueError:
            detail = response.text[:200]
        if code == RD_TORRENT_TOO_BIG:
            raise DebridError(
                "Real-Debrid refuses this torrent as too big for the account; "
                "the game needs a smaller torrent or a server-side fetch",
                too_big=True,
            )
        if code in (RD_TOO_MANY_ACTIVE, RD_TRAFFIC_EXHAUSTED, RD_FAIR_USAGE):
            raise DebridError(
                f"Real-Debrid is at a limit right now ({detail}); try again later",
                retry_later=True,
            )
        if response.status_code in (401, 403):
            raise DebridError(f"The debrid account refused the request: {detail}")
        raise DebridError(f"The debrid service answered {response.status_code}: {detail}")
