import re
import secrets
from datetime import datetime, timezone

from fastapi import HTTPException, Request, status
from pydantic import BaseModel, Field

from config import GAMEIO_SIGNUP_RATE_LIMIT
from endpoints.responses.client_token import ClientTokenCreateSchema
from handler.auth import auth_handler
from handler.database import db_user_handler
from logger.logger import log
from models.user import Role, User
from utils.client_tokens import build_create_schema, mint_client_token
from utils.google_identity import (
    GoogleIdentity,
    GoogleTokenError,
    GoogleUnavailableError,
    google_sign_in_enabled,
    verify_google_id_token,
)
from utils.rate_limit import enforce_ip_rate_limit
from utils.router import APIRouter
from utils.signup import SIGNUP_RATE_WINDOW_SECONDS, signup_is_open

GOOGLE_SIGNIN_RATE_LIMIT = 30
GOOGLE_SIGNIN_RATE_WINDOW_SECONDS = 600
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 32
USERNAME_SUFFIX_ATTEMPTS = 20

router = APIRouter(prefix="/auth/google", tags=["auth"])


class GoogleSignInPayload(BaseModel):
    id_token: str = Field(min_length=1)
    name: str = Field(min_length=1)
    scopes: list[str] = Field(min_length=1)
    expires_in: str | None = None


class GoogleSignInResponse(ClientTokenCreateSchema):
    created: bool


def _username_base(identity: GoogleIdentity) -> str:
    local_part = identity.email.split("@", 1)[0]
    base = re.sub(r"[^a-z0-9_-]", "", local_part.lower())[:USERNAME_MAX_LENGTH]
    if len(base) < USERNAME_MIN_LENGTH:
        base = f"player{base}"
    return base


def _free_username(identity: GoogleIdentity) -> str:
    base = _username_base(identity)
    if not db_user_handler.get_user_by_username(base):
        return base
    for _ in range(USERNAME_SUFFIX_ATTEMPTS):
        candidate = f"{base}{secrets.randbelow(9000) + 1000}"
        if not db_user_handler.get_user_by_username(candidate):
            return candidate
    return f"{base}-{secrets.token_hex(4)}"


def _create_account(request: Request, identity: GoogleIdentity) -> User:
    enforce_ip_rate_limit(
        request,
        bucket="signup",
        limit=GAMEIO_SIGNUP_RATE_LIMIT,
        window_seconds=SIGNUP_RATE_WINDOW_SECONDS,
        detail="Too many sign-ups from here. Try again later.",
    )
    if not signup_is_open():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign-up is closed: the server is full",
        )

    # No password was chosen, so the stored hash matches nothing anyone can type
    # until the owner sets one through the reset link sent to this address.
    user = User(
        username=_free_username(identity),
        hashed_password=auth_handler.get_password_hash(secrets.token_urlsafe(32)),
        email=identity.email,
        role=Role.USER,
    )
    created = db_user_handler.add_user(user)
    log.info(f"Account {created.id} created through Google sign-in")
    return created


@router.post("")
def sign_in_with_google(
    request: Request, payload: GoogleSignInPayload
) -> GoogleSignInResponse:
    """Trade a Google ID token for a client token.

    The account is the one holding the Google-verified address; one is made
    when none does, under the same seat limit as open sign-up. The token gets
    the requested scopes the account actually holds.

    Raises:
        HTTPException: Google sign-in is not set up
        HTTPException: The Google token is not valid
        HTTPException: The account is disabled, or sign-up is full
        HTTPException: Too many attempts from this address
        HTTPException: Google could not be reached to check the token
    """

    if not google_sign_in_enabled():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google sign-in is not set up on this server",
        )

    enforce_ip_rate_limit(
        request,
        bucket="google-signin",
        limit=GOOGLE_SIGNIN_RATE_LIMIT,
        window_seconds=GOOGLE_SIGNIN_RATE_WINDOW_SECONDS,
        detail="Too many sign-in attempts from here. Try again later.",
    )

    try:
        identity = verify_google_id_token(payload.id_token)
    except GoogleUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except GoogleTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc

    user = db_user_handler.get_user_by_email(identity.email)
    created = user is None
    if user is None:
        user = _create_account(request, identity)

    if not user.enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled"
        )

    held = {str(scope) for scope in user.oauth_scopes}
    scopes = [scope for scope in payload.scopes if scope in held]
    if not scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requested scopes exceed your permissions",
        )

    token, raw_token = mint_client_token(user, payload.name, scopes, payload.expires_in)
    now = datetime.now(timezone.utc)
    db_user_handler.update_user(user.id, {"last_login": now, "last_active": now})

    return GoogleSignInResponse(
        **build_create_schema(token, raw_token).model_dump(), created=created
    )
