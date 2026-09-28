"""Per-address throttling for endpoints anyone can reach without an account.

Counting lives in the shared cache so the limit holds across workers.
"""

from fastapi import HTTPException, Request, status
from handler.redis_handler import sync_cache


def enforce_ip_rate_limit(
    request: Request,
    bucket: str,
    limit: int,
    window_seconds: int,
    detail: str,
) -> None:
    """Allow ``limit`` calls from one address per window, then answer 429.

    The window starts at the first call and is never extended, so retries do
    not push the unlock further away. A cache failure counts as under the limit.
    """
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate:{bucket}:{client_ip}"

    try:
        count = sync_cache.incr(key)
        if count == 1:
            sync_cache.expire(key, window_seconds)
    except Exception:
        return

    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )
