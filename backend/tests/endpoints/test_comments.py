from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock

import pytest
from alembic.util import load_python_file
from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy import select
from tests.endpoints.test_catalog import _game

from handler.auth import oauth_handler
from handler.database import db_catalog_handler, db_game_comments_handler
from handler.database.base_handler import sync_session
from handler.redis_handler import sync_cache
from models.game_comment import GameComment
from models.user import User


@pytest.fixture(autouse=True)
def games():
    db_catalog_handler.upsert_games(
        [_game(1074, "Super Mario 64"), _game(3475, "Dr. Mario 64")]
    )


@pytest.fixture
def headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def viewer_headers(viewer_access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {viewer_access_token}"}


def _post(
    client: TestClient,
    headers: dict[str, str],
    body: str = "This soundtrack lives in my head 😂",
    **extra,
) -> dict:
    response = client.post(
        "/api/catalog/1074/comments", headers=headers, json={"body": body, **extra}
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_conversation_round_trip_and_author_privacy(
    client: TestClient, headers, admin_user: User
):
    first = _post(client, headers)
    second = _post(client, headers, "Still playing this every weekend", spoiler=True)
    assert first["author"] == {
        "id": admin_user.id,
        "username": admin_user.username,
        "avatar_url": None,
    }
    assert first["igdb_id"] == 1074
    assert first["can_edit"] and first["can_delete"]
    assert first["parent_id"] is None
    assert first["created_at"].endswith("+00:00")
    newest = client.get(
        "/api/catalog/1074/comments?sort=newest&limit=1", headers=headers
    ).json()
    assert newest["total"] == 2
    assert newest["items"][0]["id"] == second["id"]
    assert newest["items"][0]["spoiler"] is True
    following = client.get(
        "/api/catalog/1074/comments?sort=newest&limit=1&offset=1", headers=headers
    ).json()
    assert following["items"][0]["id"] == first["id"]
    assert (
        client.get("/api/catalog/3475/comments", headers=headers).json()["total"] == 0
    )


def test_members_can_post_and_only_edit_delete_own(
    client: TestClient, headers, viewer_headers
):
    comment = _post(client, headers)
    assert (
        client.patch(
            f"/api/comments/{comment['id']}",
            headers=viewer_headers,
            json={"body": "overwrite"},
        ).status_code
        == 403
    )
    assert (
        client.delete(
            f"/api/comments/{comment['id']}", headers=viewer_headers
        ).status_code
        == 403
    )
    own = _post(client, viewer_headers, "My first run!")
    updated = client.patch(
        f"/api/comments/{own['id']}",
        headers=viewer_headers,
        json={"body": "  My second run!  ", "spoiler": True},
    )
    assert updated.status_code == 200
    assert updated.json()["body"] == "My second run!"
    assert updated.json()["edited"] is True
    assert updated.json()["spoiler"] is True
    assert (
        client.delete(f"/api/comments/{own['id']}", headers=viewer_headers).status_code
        == 204
    )
    assert (
        client.delete(f"/api/comments/{own['id']}", headers=viewer_headers).status_code
        == 204
    )
    page = client.get("/api/catalog/1074/comments", headers=viewer_headers).json()
    assert page["total"] == 1
    assert page["items"][0]["can_edit"] is False
    assert page["items"][0]["can_delete"] is False


def test_reply_threads_are_paged_and_preserved_after_parent_delete(
    client: TestClient, headers, viewer_headers
):
    parent = _post(client, headers)
    reply = _post(client, viewer_headers, "Same 😂", parent_id=parent["id"])
    nested = _post(client, headers, "Right?", parent_id=reply["id"])
    assert nested["parent_id"] == parent["id"]
    page = client.get("/api/catalog/1074/comments", headers=headers).json()
    assert page["total"] == 1
    assert page["items"][0]["reply_count"] == 2
    replies = client.get(
        f"/api/comments/{parent['id']}/replies?limit=1", headers=headers
    ).json()
    assert replies["total"] == 2
    assert replies["items"][0]["id"] == reply["id"]
    assert (
        client.get(
            f"/api/comments/{parent['id']}/replies?limit=1&offset=1", headers=headers
        ).json()["items"][0]["id"]
        == nested["id"]
    )
    assert (
        client.delete(f"/api/comments/{parent['id']}", headers=headers).status_code
        == 204
    )
    deleted = client.get("/api/catalog/1074/comments", headers=headers).json()["items"][
        0
    ]
    assert deleted["deleted"] and deleted["body"] == "" and deleted["author"] is None
    assert deleted["reply_count"] == 2
    assert (
        client.get(f"/api/comments/{parent['id']}/replies", headers=headers).json()[
            "total"
        ]
        == 2
    )
    assert (
        client.post(
            "/api/catalog/1074/comments",
            headers=headers,
            json={"body": "reply", "parent_id": parent["id"]},
        ).status_code
        == 404
    )


def test_replies_cannot_cross_games(client: TestClient, headers):
    parent = _post(client, headers)
    response = client.post(
        "/api/catalog/3475/comments",
        headers=headers,
        json={"body": "wrong game", "parent_id": parent["id"]},
    )
    assert response.status_code == 400
    assert (
        client.post(
            "/api/catalog/1074/comments",
            headers=headers,
            json={"body": "missing parent", "parent_id": 999999},
        ).status_code
        == 404
    )


def test_likes_are_idempotent_and_top_sorts_by_likes(
    client: TestClient, headers, viewer_headers
):
    first = _post(client, headers, "First")
    second = _post(client, headers, "Second")
    path = f"/api/comments/{first['id']}/like"
    for _ in range(2):
        liked = client.put(path, headers=viewer_headers, json={"liked": True}).json()
        assert liked["like_count"] == 1 and liked["liked"] is True
    top = client.get("/api/catalog/1074/comments?sort=top", headers=headers).json()[
        "items"
    ]
    assert [item["id"] for item in top] == [first["id"], second["id"]]
    assert top[0]["liked"] is False
    for _ in range(2):
        unliked = client.put(path, headers=viewer_headers, json={"liked": False}).json()
        assert unliked["like_count"] == 0 and unliked["liked"] is False


def test_like_concurrency_does_not_duplicate(
    client: TestClient, headers, viewer_user: User
):
    comment = _post(client, headers)

    def like():
        return db_game_comments_handler.set_like(
            comment_id=comment["id"], user_id=viewer_user.id, liked=True, is_admin=False
        )

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: like(), range(4)))
    assert all(result.like_count == 1 for result in results)


def test_reports_are_private_idempotent_and_moderated(
    client: TestClient, headers, viewer_headers
):
    comment = _post(client, headers, "Bad comment")
    path = f"/api/comments/{comment['id']}/report"
    assert (
        client.put(path, headers=headers, json={"reason": "My own"}).status_code == 400
    )
    for _ in range(2):
        assert (
            client.put(
                path, headers=viewer_headers, json={"reason": "Harassment"}
            ).status_code
            == 204
        )
    assert (
        client.get("/api/comments/reports", headers=viewer_headers).status_code == 403
    )
    page = client.get("/api/comments/reports", headers=headers).json()
    assert page["total"] == 1
    report = page["items"][0]
    assert report["body_snapshot"] == "Bad comment"
    assert report["game_title"]
    assert (
        client.patch(
            f"/api/comments/{comment['id']}",
            headers=headers,
            json={"body": "Edited since report"},
        ).status_code
        == 200
    )
    assert (
        client.get("/api/comments/reports", headers=headers).json()["items"][0][
            "body_snapshot"
        ]
        == "Bad comment"
    )
    assert (
        client.patch(
            f"/api/comments/reports/{report['id']}",
            headers=viewer_headers,
            json={"action": "remove"},
        ).status_code
        == 403
    )
    assert (
        client.patch(
            f"/api/comments/reports/{report['id']}",
            headers=headers,
            json={"action": "remove"},
        ).status_code
        == 204
    )
    assert client.get("/api/comments/reports", headers=headers).json()["total"] == 0
    assert (
        client.get(
            "/api/comments/reports?report_status=removed", headers=headers
        ).json()["total"]
        == 1
    )
    assert (
        client.get("/api/catalog/1074/comments", headers=headers).json()["total"] == 0
    )


def test_report_dismissal_keeps_conversation(
    client: TestClient, headers, viewer_headers
):
    comment = _post(client, viewer_headers)
    client.put(
        f"/api/comments/{comment['id']}/report",
        headers=headers,
        json={"reason": "Check this"},
    )
    report = client.get("/api/comments/reports", headers=headers).json()["items"][0]
    assert (
        client.patch(
            f"/api/comments/reports/{report['id']}",
            headers=headers,
            json={"action": "dismiss"},
        ).status_code
        == 204
    )
    assert (
        client.get("/api/catalog/1074/comments", headers=headers).json()["total"] == 1
    )
    assert (
        client.get(
            "/api/comments/reports?report_status=dismissed", headers=headers
        ).json()["total"]
        == 1
    )
    assert (
        client.delete(f"/api/comments/{comment['id']}", headers=headers).status_code
        == 204
    )


def test_block_hides_threads_and_prevents_interactions_and_unblocks(
    client: TestClient, headers, viewer_headers, viewer_user: User
):
    own = _post(client, headers)
    other = _post(client, viewer_headers)
    _post(client, viewer_headers, "reply", parent_id=own["id"])
    for _ in range(2):
        assert (
            client.put(
                f"/api/comments/blocks/{viewer_user.id}", headers=headers
            ).status_code
            == 204
        )
    blocks = client.get("/api/comments/blocks", headers=headers).json()
    assert len(blocks) == 1 and blocks[0]["id"] == viewer_user.id
    page = client.get("/api/catalog/1074/comments", headers=headers).json()
    assert page["total"] == 1
    assert page["items"][0]["id"] == own["id"] and page["items"][0]["reply_count"] == 0
    assert (
        client.get(f"/api/comments/{other['id']}/replies", headers=headers).status_code
        == 404
    )
    assert (
        client.put(
            f"/api/comments/{other['id']}/like", headers=headers, json={"liked": True}
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/catalog/1074/comments",
            headers=viewer_headers,
            json={"body": "reply", "parent_id": own["id"]},
        ).status_code
        == 404
    )
    assert client.get("/api/comments/blocks", headers=viewer_headers).json() == []
    assert (
        client.delete(
            f"/api/comments/blocks/{viewer_user.id}", headers=headers
        ).status_code
        == 204
    )
    assert (
        client.get("/api/catalog/1074/comments", headers=headers).json()["total"] == 2
    )


def test_comment_validation_and_auth(client: TestClient, headers, admin_user: User):
    for body in ("", "   \n", "x" * 2001, "hello\u0000"):
        assert (
            client.post(
                "/api/catalog/1074/comments", headers=headers, json={"body": body}
            ).status_code
            == 422
        )
    for query in ("limit=0", "limit=51", "offset=-1", "sort=invalid"):
        assert (
            client.get(
                f"/api/catalog/1074/comments?{query}", headers=headers
            ).status_code
            == 422
        )
    assert (
        client.get("/api/catalog/999999/comments", headers=headers).status_code == 404
    )
    assert client.get("/api/catalog/1074/comments").status_code == 401
    assert (
        client.post(
            "/api/catalog/1074/comments", json={"body": "anonymous"}
        ).status_code
        == 401
    )
    assert (
        client.put(f"/api/comments/blocks/{admin_user.id}", headers=headers).status_code
        == 400
    )


def test_rate_limit_has_retry_after_and_does_not_add_extra_comment(
    client: TestClient, headers
):
    for index in range(20):
        _post(client, headers, str(index))
    response = client.post(
        "/api/catalog/1074/comments", headers=headers, json={"body": "too soon"}
    )
    assert response.status_code == 429
    assert 1 <= int(response.headers["Retry-After"]) <= 600
    assert (
        client.get("/api/catalog/1074/comments", headers=headers).json()["total"] == 20
    )


def test_rate_limit_failure_returns_retryable_error(
    client: TestClient, headers, monkeypatch
):
    def unavailable(*args, **kwargs):
        raise RedisConnectionError()

    monkeypatch.setattr(sync_cache, "pipeline", unavailable)
    response = client.post(
        "/api/catalog/1074/comments", headers=headers, json={"body": "try later"}
    )
    assert response.status_code == 503
    with sync_session() as session:
        assert session.scalar(select(GameComment.id)) is None


def test_read_only_token_cannot_change_comments(client: TestClient, admin_user: User):
    token = oauth_handler.create_access_token(
        data={"sub": admin_user.username, "iss": "romm:oauth", "scopes": "roms.read"},
        expires_delta=timedelta(minutes=5),
    )
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/catalog/1074/comments", headers=headers).status_code == 200
    assert client.get("/api/comments/reports", headers=headers).status_code == 403
    assert (
        client.patch(
            "/api/comments/reports/1", headers=headers, json={"action": "remove"}
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/catalog/1074/comments",
            headers=headers,
            json={"body": "No write permission"},
        ).status_code
        == 403
    )


def test_kiosk_guests_can_read_but_not_post(client: TestClient, monkeypatch):
    monkeypatch.setattr("handler.auth.hybrid_auth.KIOSK_MODE", True)
    assert client.get("/api/catalog/1074/comments").status_code == 200
    assert (
        client.post("/api/catalog/1074/comments", json={"body": "guest"}).status_code
        == 403
    )


def test_postgres_blob_migration_does_not_rewrite_or_delete_data(monkeypatch):
    migration = load_python_file(
        Path(__file__).parents[2] / "alembic" / "versions", "0119_asset_longblob.py"
    )
    operations = Mock()
    operations.get_bind.return_value.dialect.name = "postgresql"
    monkeypatch.setattr(migration, "op", operations)
    migration.upgrade()
    migration.downgrade()
    operations.batch_alter_table.assert_not_called()
    operations.execute.assert_not_called()


def test_mobile_admin_can_moderate_without_account_management_scope(
    client: TestClient, admin_user: User
):
    token = oauth_handler.create_access_token(
        data={
            "sub": admin_user.username,
            "iss": "romm:oauth",
            "scopes": "roms.read roms.user.write",
        },
        expires_delta=timedelta(minutes=5),
    )
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/comments/reports", headers=headers).status_code == 200
