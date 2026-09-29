import hashlib

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class ETagMiddleware:
    """Tag JSON GET responses under /api so clients revalidate them into a bodiless 304."""

    def __init__(self, app: ASGIApp, *, path_prefix: str = "/api") -> None:
        self.app = app
        self.path_prefix = path_prefix

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or scope["method"] != "GET"
            or not scope["path"].startswith(self.path_prefix)
        ):
            await self.app(scope, receive, send)
            return

        if_none_match = Headers(scope=scope).get("if-none-match")
        start: Message | None = None
        chunks: list[bytes] = []
        passthrough = False

        async def wrapped_send(message: Message) -> None:
            nonlocal start, passthrough
            if message["type"] == "http.response.start":
                headers = Headers(raw=message["headers"])
                cacheable = (
                    message["status"] == 200
                    and headers.get("content-type", "").startswith("application/json")
                    and "etag" not in headers
                    and "cache-control" not in headers
                    and "content-encoding" not in headers
                )
                if not cacheable:
                    passthrough = True
                    await send(message)
                    return
                start = message
                return

            if passthrough or message["type"] != "http.response.body":
                await send(message)
                return

            chunks.append(message.get("body", b""))
            if message.get("more_body", False):
                return

            if start is None:
                return
            body = b"".join(chunks)
            etag = f'W/"{hashlib.blake2b(body, digest_size=16).hexdigest()}"'
            headers = MutableHeaders(raw=start["headers"])
            headers["etag"] = etag
            headers["cache-control"] = "private, no-cache"

            if if_none_match and _matches(if_none_match, etag):
                del headers["content-length"]
                del headers["content-type"]
                await send({**start, "status": 304, "headers": headers.raw})
                await send({"type": "http.response.body", "body": b""})
                return

            await send(start)
            await send({"type": "http.response.body", "body": body})

        await self.app(scope, receive, wrapped_send)


def _matches(if_none_match: str, etag: str) -> bool:
    if if_none_match.strip() == "*":
        return True
    opaque = etag.removeprefix("W/")
    return any(
        candidate.strip().removeprefix("W/") == opaque
        for candidate in if_none_match.split(",")
    )
