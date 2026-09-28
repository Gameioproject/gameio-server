"""Per-address throttling for the endpoints anyone can reach without an account.

Counting lives in the shared cache rather than in process memory so the limit
still holds when the app runs several workers, which it does in production.
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

    A cache that is down must not lock people out of signing up, so a failure
    to count is treated as being under the limit.
    """
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate:{bucket}:{client_ip}"

    try:
        pipe = sync_cache.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds)
        count, _ = pipe.execute()
    except Exception:
        return

    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )
