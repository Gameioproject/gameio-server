import time

import pytest
from fastapi import status
from joserfc import jwt
from joserfc.jwk import KeySet, RSAKey

from handler.auth import auth_handler
from handler.database import db_client_token_handler, db_user_handler
from models.user import Role, User
from utils import google_identity

CLIENT_ID = "1234-web.apps.googleusercontent.com"
SCOPES = ["me.read", "roms.read"]


@pytest.fixture(scope="module")
def signing_key():
    return RSAKey.generate_key(2048, parameters={"kid": "test-kid"})


@pytest.fixture(autouse=True)
def google_configured(monkeypatch, signing_key):
    monkeypatch.setattr(google_identity, "GOOGLE_CLIENT_IDS", [CLIENT_ID])
    monkeypatch.setattr(
        google_identity.google_keys, "get", lambda kid: KeySet([signing_key])
    )


@pytest.fixture
def existing_user(admin_user):
    return db_user_handler.update_user(admin_user.id, {"email": "admin@example.com"})


def make_token(key, **overrides):
    now = int(time.time())
    claims = {
        "iss": "https://accounts.google.com",
        "aud": CLIENT_ID,
        "azp": "1234-android.apps.googleusercontent.com",
        "sub": "10987654321",
        "email": "New.Player@gmail.com",
        "email_verified": True,
        "name": "New Player",
        "iat": now,
        "exp": now + 3600,
    }
    claims.update(overrides)
    claims = {k: v for k, v in claims.items() if v is not None}
    return jwt.encode({"alg": "RS256", "kid": "test-kid"}, claims, key)


def sign_in(client, id_token, scopes=SCOPES):
    return client.post(
        "/api/auth/google",
        json={"id_token": id_token, "name": "Retroid Pocket 5", "scopes": scopes},
    )


def test_creates_account_for_new_address(client, signing_key):
    response = sign_in(client, make_token(signing_key))

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["created"] is True
    assert body["raw_token"].startswith("rmm_")
    assert set(body["scopes"]) == set(SCOPES)

    user = db_user_handler.get_user_by_email("new.player@gmail.com")
    assert user is not None
    assert user.username == "newplayer"
    assert user.role == Role.USER
    assert body["user_id"] == user.id

    me = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {body['raw_token']}"}
    )
    assert me.status_code == status.HTTP_200_OK
    assert me.json()["username"] == "newplayer"


def test_signs_in_existing_account_by_email(client, signing_key, existing_user):
    token = make_token(signing_key, email=existing_user.email.upper())

    response = sign_in(client, token)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["created"] is False
    assert response.json()["user_id"] == existing_user.id
    assert len(db_user_handler.get_users()) == 1


def test_second_sign_in_reuses_the_account(client, signing_key):
    first = sign_in(client, make_token(signing_key))
    second = sign_in(client, make_token(signing_key))

    assert second.json()["created"] is False
    assert second.json()["user_id"] == first.json()["user_id"]
    assert len(db_client_token_handler.get_tokens_by_user(first.json()["user_id"])) == 2


def test_taken_username_gets_a_suffix(client, signing_key):
    db_user_handler.add_user(
        User(
            username="newplayer",
            hashed_password=auth_handler.get_password_hash("password"),
            email="someone.else@example.com",
            role=Role.USER,
        )
    )

    response = sign_in(client, make_token(signing_key))

    user = db_user_handler.get_user(response.json()["user_id"])
    assert user.username.startswith("newplayer")
    assert user.username != "newplayer"


def test_new_account_cannot_sign_in_with_a_guessed_password(client, signing_key):
    sign_in(client, make_token(signing_key))

    assert auth_handler.authenticate_user("newplayer", "") is None


def test_scopes_are_narrowed_to_what_the_account_holds(client, signing_key):
    response = sign_in(
        client, make_token(signing_key), scopes=["roms.read", "users.write"]
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["scopes"] == ["roms.read"]


@pytest.mark.parametrize(
    "overrides",
    [
        {"aud": "someone-elses-app.apps.googleusercontent.com"},
        {"iss": "https://evil.example.com"},
        {"exp": int(time.time()) - 3600},
        {"email_verified": False},
        {"email_verified": None},
        {"email": None},
    ],
)
def test_rejects_invalid_tokens(client, signing_key, overrides):
    response = sign_in(client, make_token(signing_key, **overrides))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert db_user_handler.get_user_by_email("new.player@gmail.com") is None


def test_rejects_token_signed_by_another_key(client):
    forged = RSAKey.generate_key(2048, parameters={"kid": "test-kid"})

    response = sign_in(client, make_token(forged))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_rejects_garbage(client):
    assert sign_in(client, "not-a-jwt").status_code == status.HTTP_401_UNAUTHORIZED


def test_disabled_account_is_refused(client, signing_key, existing_user):
    db_user_handler.update_user(existing_user.id, {"enabled": False})

    response = sign_in(client, make_token(signing_key, email=existing_user.email))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_full_server_refuses_new_accounts(client, signing_key, monkeypatch):
    monkeypatch.setattr("endpoints.google_auth.signup_is_open", lambda: False)

    response = sign_in(client, make_token(signing_key))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert db_user_handler.get_user_by_email("new.player@gmail.com") is None


def test_full_server_still_signs_in_existing_accounts(
    client, signing_key, existing_user, monkeypatch
):
    monkeypatch.setattr("endpoints.google_auth.signup_is_open", lambda: False)

    response = sign_in(client, make_token(signing_key, email=existing_user.email))

    assert response.status_code == status.HTTP_200_OK


def test_not_configured(client, signing_key, monkeypatch):
    monkeypatch.setattr(google_identity, "GOOGLE_CLIENT_IDS", [])
    monkeypatch.setattr("endpoints.google_auth.google_sign_in_enabled", lambda: False)

    response = sign_in(client, make_token(signing_key))

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_heartbeat_advertises_the_client_id(client):
    response = client.get("/api/heartbeat")

    assert response.json()["FRONTEND"]["GOOGLE_CLIENT_ID"] == CLIENT_ID


class FakeCertsResponse:
    def __init__(self, keys):
        self.keys = keys
        self.headers = {"cache-control": "public, max-age=3600"}

    def raise_for_status(self):
        pass

    def json(self):
        return KeySet(self.keys).as_dict()


def test_key_cache_fetches_once_and_again_for_a_new_kid(monkeypatch):
    first = RSAKey.generate_key(2048, parameters={"kid": "first"})
    second = RSAKey.generate_key(2048, parameters={"kid": "second"})
    published = [first]
    fetches = []

    def fake_get(url, timeout):
        fetches.append(url)
        return FakeCertsResponse(list(published))

    monkeypatch.setattr(google_identity.httpx, "get", fake_get)
    cache = google_identity._GoogleKeyCache()

    cache.get("first")
    cache.get("first")
    assert len(fetches) == 1

    published.append(second)
    cache._fetched_at -= google_identity.MIN_REFETCH_INTERVAL_SECONDS
    keys = cache.get("second")
    assert len(fetches) == 2
    assert keys.get_by_kid("second") is not None


def test_key_cache_keeps_old_keys_when_google_is_unreachable(monkeypatch):
    key = RSAKey.generate_key(2048, parameters={"kid": "only"})
    monkeypatch.setattr(
        google_identity.httpx, "get", lambda url, timeout: FakeCertsResponse([key])
    )
    cache = google_identity._GoogleKeyCache()
    cache.get("only")
    cache._fetched_at -= google_identity.MIN_REFETCH_INTERVAL_SECONDS

    def unreachable(url, timeout):
        raise google_identity.httpx.ConnectError("down")

    monkeypatch.setattr(google_identity.httpx, "get", unreachable)

    assert cache.get("unknown").get_by_kid("only") is not None


def test_key_cache_without_keys_reports_google_unreachable(monkeypatch):
    def unreachable(url, timeout):
        raise google_identity.httpx.ConnectError("down")

    monkeypatch.setattr(google_identity.httpx, "get", unreachable)

    with pytest.raises(google_identity.GoogleUnavailableError):
        google_identity._GoogleKeyCache().get("any")


def test_unknown_kid_does_not_refetch_within_a_minute(monkeypatch):
    key = RSAKey.generate_key(2048, parameters={"kid": "only"})
    fetches = []

    def fake_get(url, timeout):
        fetches.append(url)
        return FakeCertsResponse([key])

    monkeypatch.setattr(google_identity.httpx, "get", fake_get)
    cache = google_identity._GoogleKeyCache()

    cache.get("only")
    cache.get("forged-1")
    cache.get("forged-2")

    assert len(fetches) == 1


def test_google_unreachable_answers_503(client, signing_key, monkeypatch):
    def unreachable(kid):
        raise google_identity.GoogleUnavailableError("down")

    monkeypatch.setattr(google_identity.google_keys, "get", unreachable)

    response = sign_in(client, make_token(signing_key))

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
