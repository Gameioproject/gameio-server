import pytest
from fastapi import status

from handler.database import db_collection_handler
from models.collection import Collection
from models.user import User


@pytest.fixture
def collection(admin_user: User) -> Collection:
    return db_collection_handler.add_collection(
        Collection(
            name="Test Collection",
            description="A test collection",
            is_public=False,
            is_favorite=False,
            user_id=admin_user.id,
        )
    )


@pytest.fixture
def public_collection(editor_user: User) -> Collection:
    return db_collection_handler.add_collection(
        Collection(
            name="Shared picks",
            description="",
            is_public=True,
            is_favorite=False,
            user_id=editor_user.id,
        )
    )


class TestCollectionEndpoints:
    def test_requires_auth(self, client):
        assert (
            client.get("/api/collections").status_code == status.HTTP_401_UNAUTHORIZED
        )

    def test_creates_collection(self, client, access_token: str):
        response = client.post(
            "/api/collections",
            headers={"Authorization": f"Bearer {access_token}"},
            data={"name": "Speedruns", "description": "Fast ones"},
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["name"] == "Speedruns"
        assert body["description"] == "Fast ones"
        assert body["is_favorite"] is False
        assert body["game_igdb_ids"] == []
        assert body["game_count"] == 0
        assert body["url_covers"] == []

    def test_duplicate_name_returns_conflict(
        self, client, access_token: str, collection: Collection
    ):
        response = client.post(
            "/api/collections",
            headers={"Authorization": f"Bearer {access_token}"},
            data={"name": collection.name, "description": ""},
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_lists_own_and_public_collections(
        self,
        client,
        access_token: str,
        collection: Collection,
        public_collection: Collection,
        editor_user: User,
    ):
        private_other = db_collection_handler.add_collection(
            Collection(
                name="Private picks",
                description="",
                is_public=False,
                user_id=editor_user.id,
            )
        )
        response = client.get(
            "/api/collections", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        names = {c["name"] for c in response.json()}
        assert collection.name in names
        assert public_collection.name in names
        assert private_other.name not in names

    def test_get_and_delete_own_collection(
        self, client, access_token: str, collection: Collection
    ):
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get(f"/api/collections/{collection.id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == collection.id

        response = client.delete(f"/api/collections/{collection.id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert db_collection_handler.get_collection(collection.id) is None

    def test_cannot_delete_other_users_collection(
        self, client, editor_access_token: str, collection: Collection
    ):
        response = client.delete(
            f"/api/collections/{collection.id}",
            headers={"Authorization": f"Bearer {editor_access_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert db_collection_handler.get_collection(collection.id) is not None

    def test_returns_404_for_missing_collection(self, client, access_token: str):
        response = client.get(
            "/api/collections/999999",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_smart_and_virtual_collections_are_empty(self, client, access_token: str):
        # Classic clients still ask; they get nothing rather than an error.
        headers = {"Authorization": f"Bearer {access_token}"}
        assert client.get("/api/collections/smart", headers=headers).json() == []
        assert client.get("/api/collections/virtual", headers=headers).json() == []
