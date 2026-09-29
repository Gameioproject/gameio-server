"""Verifying Google ID tokens without a Google library.

Google signs ID tokens with rotating RSA keys published as a JWK set. The set is
cached for as long as Google's Cache-Control allows and fetched again when a
token names a key the cache does not hold yet.
"""

import re
import threading
import time
from dataclasses import dataclass

import httpx
from joserfc import jwt
from joserfc.errors import JoseError
from joserfc.jwk import KeySet

from config import GOOGLE_CLIENT_IDS

GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = ["accounts.google.com", "https://accounts.google.com"]
DEFAULT_CERTS_MAX_AGE_SECONDS = 3600
CERTS_FETCH_TIMEOUT_SECONDS = 10
CLOCK_SKEW_SECONDS = 60
MIN_REFETCH_INTERVAL_SECONDS = 60

_MAX_AGE = re.compile(r"max-age=(\d+)")


class GoogleTokenError(Exception):
    pass


class GoogleUnavailableError(GoogleTokenError):
    pass


@dataclass(frozen=True)
class GoogleIdentity:
    subject: str
    email: str
    name: str | None


class _GoogleKeyCache:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._keys: KeySet | None = None
        self._expires_at = 0.0
        self._fetched_at = 0.0

    def get(self, kid: str | None) -> KeySet:
        with self._lock:
            now = time.monotonic()
            stale = self._keys is None or now >= self._expires_at
            # An unknown kid usually means Google rotated keys, but a forged token
            # can name any kid, so it may not trigger a fetch more than once a minute.
            rotated = (
                not self._holds(kid)
                and now - self._fetched_at >= MIN_REFETCH_INTERVAL_SECONDS
            )
            if stale or rotated:
                self._refresh()
            assert self._keys is not None
            return self._keys

    def _holds(self, kid: str | None) -> bool:
        if self._keys is None or kid is None:
            return False
        return any(key.kid == kid for key in self._keys.keys)

    def _refresh(self) -> None:
        self._fetched_at = time.monotonic()
        try:
            response = httpx.get(GOOGLE_CERTS_URL, timeout=CERTS_FETCH_TIMEOUT_SECONDS)
            response.raise_for_status()
            keys = KeySet.import_key_set(response.json())
        except (httpx.HTTPError, ValueError, JoseError) as exc:
            if self._keys is not None:
                return
            raise GoogleUnavailableError(
                "Could not reach Google to check the sign-in"
            ) from exc

        match = _MAX_AGE.search(response.headers.get("cache-control", ""))
        max_age = int(match.group(1)) if match else DEFAULT_CERTS_MAX_AGE_SECONDS
        self._keys = keys
        self._expires_at = time.monotonic() + max_age


google_keys = _GoogleKeyCache()


def google_sign_in_enabled() -> bool:
    return bool(GOOGLE_CLIENT_IDS)


def google_web_client_id() -> str | None:
    """The client id apps ask Google to issue ID tokens for."""
    return GOOGLE_CLIENT_IDS[0] if GOOGLE_CLIENT_IDS else None


def verify_google_id_token(id_token: str) -> GoogleIdentity:
    """Check the token's signature and claims and return who it names.

    Raises:
        GoogleTokenError: The token is malformed, forged, expired, meant for
            another app, or names an address Google has not verified.
    """
    if not google_sign_in_enabled():
        raise GoogleTokenError("Google sign-in is not set up on this server")

    try:
        token = jwt.decode(
            id_token,
            lambda obj: google_keys.get(obj.headers().get("kid")),
            algorithms=["RS256"],
        )
        jwt.JWTClaimsRegistry(
            leeway=CLOCK_SKEW_SECONDS,
            iss={"essential": True, "values": GOOGLE_ISSUERS},
            aud={"essential": True, "values": GOOGLE_CLIENT_IDS},
            exp={"essential": True},
            sub={"essential": True},
            email={"essential": True},
        ).validate(token.claims)
    except GoogleUnavailableError:
        raise
    except (JoseError, ValueError, KeyError) as exc:
        raise GoogleTokenError("Google token is not valid") from exc

    claims = token.claims
    if claims.get("email_verified") not in (True, "true"):
        raise GoogleTokenError("Google has not verified this email address")

    return GoogleIdentity(
        subject=str(claims["sub"]),
        email=str(claims["email"]).lower(),
        name=claims.get("name"),
    )
