from unittest.mock import Mock, patch

import pytest
from fastapi import status

from handler.database import db_game_source_handler
from models.game_source import GameHost, GameHostKind


@pytest.fixture
def ia_host() -> GameHost:
    return db_game_source_handler.add_host(
        name="My N64 item",
        kind=GameHostKind.INTERNET_ARCHIVE,
        base="my-n64-roms",
        platform_slug="n64",
    )


class TestHostEndpoints:
    def test_list_requires_auth(self, client):
        assert client.get("/api/hosts").status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_list_delete(self, client, access_token: str):
        response = client.post(
            "/api/hosts",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "My N64 item",
                "kind": "internet_archive",
                "base": "my-n64-roms",
                "platform_slug": "n64",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        host = response.json()
        assert host["kind"] == "internet_archive"
        assert host["source_count"] == 0
        assert host["enabled"] is True

        response = client.get(
            "/api/hosts", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert [h["id"] for h in response.json()] == [host["id"]]

        response = client.delete(
            f"/api/hosts/{host['id']}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert db_game_source_handler.get_hosts() == []

    def test_update_host(self, client, access_token: str, ia_host: GameHost):
        response = client.patch(
            f"/api/hosts/{ia_host.id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"enabled": False, "name": "Renamed", "platform_slug": ""},
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["enabled"] is False
        assert body["name"] == "Renamed"
        assert body["platform_slug"] is None
        assert body["indexing"] is False
        assert body["last_index_stats"] is None

    def test_delete_missing(self, client, access_token: str):
        response = client.delete(
            "/api/hosts/999", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_requires_write_scope(self, client, viewer_access_token: str):
        response = client.post(
            "/api/hosts",
            headers={"Authorization": f"Bearer {viewer_access_token}"},
            json={"name": "x", "kind": "http", "base": "https://x.test"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_index_enqueues_task(self, client, access_token: str, ia_host: GameHost):
        job = Mock()
        job.id = "job-1"
        with patch(
            "endpoints.hosts.low_prio_queue.enqueue", return_value=job
        ) as enqueue:
            response = client.post(
                f"/api/hosts/{ia_host.id}/index",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"task_id": "job-1", "host_id": ia_host.id}
        assert enqueue.call_args.kwargs["kwargs"] == {"host_id": ia_host.id}
        listed = client.get(
            "/api/hosts", headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        assert listed[0]["indexing"] is True

        # A second request while the job runs is refused.
        with patch("endpoints.hosts.low_prio_queue.enqueue", return_value=job):
            response = client.post(
                f"/api/hosts/{ia_host.id}/index",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        assert response.status_code == status.HTTP_409_CONFLICT

        db_game_source_handler.mark_index_finished(ia_host.id, {"matched": 1})
        listed = client.get(
            "/api/hosts", headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        assert listed[0]["indexing"] is False
        assert listed[0]["last_index_stats"] == {"matched": 1}
        assert listed[0]["last_indexed_at"] is not None

    def test_index_rejects_plain_http_host(self, client, access_token: str):
        host = db_game_source_handler.add_host(
            name="Plain", kind=GameHostKind.HTTP, base="https://files.test/roms"
        )
        response = client.post(
            f"/api/hosts/{host.id}/index",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_index_missing_host(self, client, access_token: str):
        response = client.post(
            "/api/hosts/999/index",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestInternetArchiveLinks:
    def test_create_accepts_item_links(self, client, access_token: str):
        response = client.post(
            "/api/hosts",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "PS2",
                "kind": "internet_archive",
                "base": "https://archive.org/download/RedumpSonyPS2NTSCUPart2/",
            },
        )
        assert response.status_code == 200, response.text
        assert response.json()["base"] == "RedumpSonyPS2NTSCUPart2"

    def test_create_rejects_other_links(self, client, access_token: str):
        response = client.post(
            "/api/hosts",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "Elsewhere",
                "kind": "internet_archive",
                "base": "https://example.com/roms",
            },
        )
        assert response.status_code == 422
