from collections.abc import Sequence

from pydantic import ConfigDict

from models.collection import Collection

from .base import BaseModel, UTCDatetime


class CollectionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    game_igdb_ids: list[int] = []
    rom_ids: list[int] = []
    game_count: int = 0
    url_covers: list[str] = []
    url_cover: str | None
    path_cover_small: str | None
    path_cover_large: str | None
    is_public: bool = False
    is_favorite: bool = False
    user_id: int
    owner_username: str
    created_at: UTCDatetime
    updated_at: UTCDatetime

    @classmethod
    def for_user(
        cls, user_id: int, collections: Sequence["Collection"]
    ) -> list["CollectionSchema"]:
        return [
            cls.model_validate(c)
            for c in collections
            if c.user_id == user_id or c.is_public
        ]
