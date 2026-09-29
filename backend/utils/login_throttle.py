"""Throttling for every place a password is checked.

Only failed attempts count, so a player who types their password right is never
slowed down. Two ceilings apply: one per address, which stops a single machine
guessing, and a looser one per account, which caps guessing spread across many
addresses without letting one stranger lock a player out. A cache failure
counts as under the limit.
"""

from fastapi import HTTPException, status
from starlette.requests import HTTPConnection

from handler.auth import auth_handler
from handler.auth.constants import LOGIN_THROTTLED_DETAIL
from handler.redis_handler import sync_cache
from models.user import User

LOGIN_WINDOW_SECONDS = 900
LOGIN_FAILURES_PER_ADDRESS = 20
LOGIN_FAILURES_PER_ACCOUNT = 50


def _keys(conn: HTTPConnection, username: str) -> tuple[str, str]:
    client_ip = conn.client.host if conn.client else "unknown"
    account = username.strip().lower()
    return f"login-fail:ip:{client_ip}", f"login-fail:user:{account}"


def login_is_throttled(conn: HTTPConnection, username: str) -> bool:
    address_key, account_key = _keys(conn, username)
    try:
        address_failures, account_failures = sync_cache.mget(address_key, account_key)
    except Exception:
        return False
    return (
        int(address_failures or 0) >= LOGIN_FAILURES_PER_ADDRESS
        or int(account_failures or 0) >= LOGIN_FAILURES_PER_ACCOUNT
    )


def record_login_failure(conn: HTTPConnection, username: str) -> None:
    for key in _keys(conn, username):
        try:
            if sync_cache.incr(key) == 1:
                sync_cache.expire(key, LOGIN_WINDOW_SECONDS)
        except Exception:
            return


def authenticate_or_throttle(
    conn: HTTPConnection, username: str, password: str
) -> User | None:
    """Check a password, answering 429 once too many attempts have failed.

    Blocking: call it from a sync endpoint or through a threadpool.
    """
    if login_is_throttled(conn, username):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=LOGIN_THROTTLED_DETAIL,
        )
    user = auth_handler.authenticate_user(username, password)
    if user is None:
        record_login_failure(conn, username)
    return user
