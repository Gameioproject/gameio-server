import time
from typing import Literal

from fastapi import HTTPException, status
from redis.exceptions import RedisError

from handler.redis_handler import sync_cache

COMMENT_RATE_LIMITS = {
    "post": (20, 600),
    "edit": (30, 60),
    "like": (120, 60),
    "report": (10, 600),
    "block": (30, 60),
}


def check_comment_rate_limit(
    user_id: int, action: Literal["post", "edit", "like", "report", "block"]
) -> None:
    limit, window = COMMENT_RATE_LIMITS[action]
    now = int(time.time())
    key = f"comments:rate:{action}:{user_id}:{now // window}"
    try:
        with sync_cache.pipeline(transaction=True) as pipeline:
            pipeline.incr(key)
            pipeline.expire(key, window * 2)
            count, _ = pipeline.execute()
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Comments are temporarily unavailable. Try again shortly.",
        ) from None
    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait before trying again.",
            headers={"Retry-After": str(window - now % window)},
        )
