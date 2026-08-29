from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import FRONTEND_RESOURCES_PATH
from models.base import BaseModel

if TYPE_CHECKING:
    from models.catalog import CatalogGame
    from models.user import User


class Collection(BaseModel):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(length=400))
    description: Mapped[str | None] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(default=False)
    is_favorite: Mapped[bool] = mapped_column(default=False)
    path_cover_l: Mapped[str | None] = mapped_column(Text, default="")
    path_cover_s: Mapped[str | None] = mapped_column(Text, default="")
    url_cover: Mapped[str | None] = mapped_column(
        Text, default="", doc="URL of cover pulled from metadata providers"
    )

    # Catalog games in the collection; owning a game is not required.
    games: Mapped[list["CatalogGame"]] = relationship(
        "CatalogGame",
        secondary="collections_games",
        lazy="selectin",
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(lazy="joined", back_populates="collections")

    @property
    def owner_username(self) -> str:
        return self.user.username

    @property
    def game_igdb_ids(self) -> list[int]:
        return sorted(g.igdb_id for g in self.games)

    @property
    def game_count(self) -> int:
        return len(self.games)

    @property
    def rom_ids(self) -> list[int]:
        """Classic per-platform ids, for clients that still speak the ROM library API."""
        from handler.compat.argosy import rom_id

        return sorted(
            rid
            for g in self.games
            for slug in g.platform_slugs
            if (rid := rom_id(g.id, slug)) is not None
        )

    @property
    def url_covers(self) -> list[str]:
        return [g.url_cover_small for g in self.games if g.url_cover_small]

    @property
    def fs_resources_path(self) -> str:
        return f"collections/{str(self.id)}"

    @property
    def path_cover_small(self) -> str | None:
        return (
            f"{FRONTEND_RESOURCES_PATH}/{self.path_cover_s}?ts={self.updated_at}"
            if self.path_cover_s
            else None
        )

    @property
    def path_cover_large(self) -> str | None:
        return (
            f"{FRONTEND_RESOURCES_PATH}/{self.path_cover_l}?ts={self.updated_at}"
            if self.path_cover_l
            else None
        )

    def __repr__(self) -> str:
        return self.name


class CollectionGame(BaseModel):
    __tablename__ = "collections_games"

    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True
    )
    catalog_game_id: Mapped[int] = mapped_column(
        ForeignKey("catalog_games.id", ondelete="CASCADE"), primary_key=True
    )
