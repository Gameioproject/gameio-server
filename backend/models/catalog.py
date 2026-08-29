from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel
from utils.database import CustomJSON

CATALOG_NAME_MAX_LENGTH = 400
CATALOG_SLUG_MAX_LENGTH = 100
CATALOG_IMAGE_ID_MAX_LENGTH = 64
CATALOG_URL_MAX_LENGTH = 1000

IGDB_IMAGE_BASE_URL = "https://images.igdb.com/igdb/image/upload"
IGDB_COVER_SIZE = "t_1080p"
IGDB_COVER_SMALL_SIZE = "t_cover_big"
IGDB_SCREENSHOT_SIZE = "t_720p"


def igdb_image_url(image_id: str, size: str) -> str:
    return f"{IGDB_IMAGE_BASE_URL}/{size}/{image_id}.jpg"


class CatalogGame(BaseModel):
    """A game known from the metadata catalog, whether or not a ROM exists for it."""

    __tablename__ = "catalog_games"
    __table_args__ = (
        Index("idx_catalog_games_name", "name"),
        Index("idx_catalog_games_rating", "rating", "rating_count"),
        Index("idx_catalog_games_release_year", "release_year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    igdb_id: Mapped[int] = mapped_column(Integer, unique=True)

    name: Mapped[str] = mapped_column(String(length=CATALOG_NAME_MAX_LENGTH))
    slug: Mapped[str | None] = mapped_column(String(length=CATALOG_NAME_MAX_LENGTH))
    summary: Mapped[str | None] = mapped_column(Text)
    release_year: Mapped[int | None] = mapped_column(Integer)
    # Unix seconds, as IGDB reports it.
    first_release_date: Mapped[int | None] = mapped_column(Integer)

    cover_image_id: Mapped[str | None] = mapped_column(
        String(length=CATALOG_IMAGE_ID_MAX_LENGTH)
    )
    screenshot_image_ids: Mapped[list[str]] = mapped_column(CustomJSON(), default=[])

    # IGDB total_rating, 0-100.
    rating: Mapped[float | None] = mapped_column(Float)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)

    youtube_video_id: Mapped[str | None] = mapped_column(
        String(length=CATALOG_IMAGE_ID_MAX_LENGTH)
    )
    igdb_url: Mapped[str | None] = mapped_column(String(length=CATALOG_URL_MAX_LENGTH))
    # Unix seconds of the source's last update, to skip unchanged rows on re-import.
    source_updated_at: Mapped[int | None] = mapped_column(Integer)

    platforms: Mapped[list[CatalogGamePlatform]] = relationship(
        back_populates="game", cascade="all, delete-orphan", lazy="selectin"
    )
    genre_links: Mapped[list[CatalogGameGenre]] = relationship(
        back_populates="game", cascade="all, delete-orphan", lazy="selectin"
    )

    @property
    def platform_slugs(self) -> list[str]:
        return sorted(p.platform_slug for p in self.platforms)

    @property
    def genres(self) -> list[str]:
        return sorted(g.genre for g in self.genre_links)

    @property
    def url_cover(self) -> str | None:
        if not self.cover_image_id:
            return None
        return igdb_image_url(self.cover_image_id, IGDB_COVER_SIZE)

    @property
    def url_cover_small(self) -> str | None:
        if not self.cover_image_id:
            return None
        return igdb_image_url(self.cover_image_id, IGDB_COVER_SMALL_SIZE)

    @property
    def url_screenshots(self) -> list[str]:
        return [
            igdb_image_url(image_id, IGDB_SCREENSHOT_SIZE)
            for image_id in self.screenshot_image_ids or []
        ]

    def __repr__(self) -> str:
        return f"{self.name} (igdb:{self.igdb_id})"


class CatalogGamePlatform(BaseModel):
    """Platform membership of a catalog game, keyed by RomM's universal platform slug."""

    __tablename__ = "catalog_game_platforms"
    __table_args__ = (
        UniqueConstraint(
            "catalog_game_id", "platform_slug", name="unique_catalog_game_platform"
        ),
        Index("idx_catalog_game_platforms_slug", "platform_slug", "catalog_game_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    catalog_game_id: Mapped[int] = mapped_column(
        ForeignKey("catalog_games.id", ondelete="CASCADE")
    )
    platform_slug: Mapped[str] = mapped_column(String(length=CATALOG_SLUG_MAX_LENGTH))

    game: Mapped[CatalogGame] = relationship(back_populates="platforms")


class CatalogGameGenre(BaseModel):
    __tablename__ = "catalog_game_genres"
    __table_args__ = (
        UniqueConstraint("catalog_game_id", "genre", name="unique_catalog_game_genre"),
        Index("idx_catalog_game_genres_genre", "genre", "catalog_game_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    catalog_game_id: Mapped[int] = mapped_column(
        ForeignKey("catalog_games.id", ondelete="CASCADE")
    )
    genre: Mapped[str] = mapped_column(String(length=CATALOG_SLUG_MAX_LENGTH))

    game: Mapped[CatalogGame] = relationship(back_populates="genre_links")
