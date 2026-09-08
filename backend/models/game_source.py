from __future__ import annotations

import enum
from datetime import datetime
from typing import Any
from urllib.parse import quote

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel
from models.catalog import CatalogGame
from utils.database import CustomJSON

HOST_NAME_MAX_LENGTH = 200
HOST_BASE_MAX_LENGTH = 1000
SOURCE_PATH_MAX_LENGTH = 1000
SOURCE_FILENAME_MAX_LENGTH = 500
SOURCE_REGION_MAX_LENGTH = 100
PLATFORM_SLUG_MAX_LENGTH = 100

INTERNET_ARCHIVE_DOWNLOAD_URL = "https://archive.org/download"


class GameHostKind(enum.StrEnum):
    INTERNET_ARCHIVE = "internet_archive"
    HTTP = "http"
    # A torrent (MiNERVA Archive): files are resolved to links through a debrid account.
    TORRENT = "torrent"


class GameHost(BaseModel):
    """A remote file host the server can resolve download links against."""

    __tablename__ = "game_hosts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=HOST_NAME_MAX_LENGTH))
    kind: Mapped[GameHostKind] = mapped_column(Enum(GameHostKind))
    # Internet Archive item identifier, a base URL for plain HTTP hosts, or the
    # listing directory / .torrent link of a torrent host.
    base: Mapped[str] = mapped_column(String(length=HOST_BASE_MAX_LENGTH))
    # Torrent hosts: the info hash learnt from the torrent file when indexing.
    info_hash: Mapped[str | None] = mapped_column(String(length=40))
    # Platform assumed for files whose path does not name one.
    platform_slug: Mapped[str | None] = mapped_column(
        String(length=PLATFORM_SLUG_MAX_LENGTH)
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    # Set while an index job runs, so the UI can show progress without polling RQ.
    index_started_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    last_indexed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    last_index_stats: Mapped[dict[str, Any] | None] = mapped_column(CustomJSON())

    sources: Mapped[list[GameSource]] = relationship(
        back_populates="host", cascade="all, delete-orphan"
    )

    def url_for(self, path: str) -> str:
        quoted = quote(path, safe="/")
        if self.kind == GameHostKind.INTERNET_ARCHIVE:
            return f"{INTERNET_ARCHIVE_DOWNLOAD_URL}/{self.base}/{quoted}"
        if self.kind == GameHostKind.TORRENT:
            # Not fetchable as is: the download endpoints resolve it through debrid.
            return f"magnet:?xt=urn:btih:{self.info_hash or ''}&dn={quote(self.name)}"
        return f"{self.base.rstrip('/')}/{quoted}"

    def __repr__(self) -> str:
        return f"{self.name} ({self.kind}:{self.base})"


class GameSource(BaseModel):
    """One downloadable file for a catalog game on a host. Owning a game means having one."""

    __tablename__ = "game_sources"
    __table_args__ = (
        UniqueConstraint("host_id", "path", name="unique_game_source_host_path"),
        # Explicit B-tree index on host_id: the composite unique above becomes a
        # HASH index on MariaDB (utf8mb4 key length) and cannot back the FK.
        Index("idx_game_sources_host", "host_id"),
        Index("idx_game_sources_game", "catalog_game_id", "id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    catalog_game_id: Mapped[int] = mapped_column(
        ForeignKey("catalog_games.id", ondelete="CASCADE")
    )
    host_id: Mapped[int] = mapped_column(
        ForeignKey("game_hosts.id", ondelete="CASCADE")
    )
    # Relative to the host; the host builds the absolute URL.
    path: Mapped[str] = mapped_column(String(length=SOURCE_PATH_MAX_LENGTH))
    filename: Mapped[str] = mapped_column(String(length=SOURCE_FILENAME_MAX_LENGTH))
    platform_slug: Mapped[str] = mapped_column(String(length=PLATFORM_SLUG_MAX_LENGTH))
    size: Mapped[int | None] = mapped_column(BigInteger)
    md5: Mapped[str | None] = mapped_column(String(length=32))
    sha1: Mapped[str | None] = mapped_column(String(length=40))
    region: Mapped[str | None] = mapped_column(String(length=SOURCE_REGION_MAX_LENGTH))
    # Torrent hosts: the file's position in the torrent, MiNERVA's "so_id".
    file_index: Mapped[int | None] = mapped_column(Integer)

    game: Mapped[CatalogGame] = relationship(lazy="joined")
    host: Mapped[GameHost] = relationship(back_populates="sources", lazy="joined")

    @property
    def url(self) -> str:
        return self.host.url_for(self.path)

    @property
    def magnet(self) -> str | None:
        """A "select only" magnet for this file, when its host is a torrent (BEP 53)."""
        if self.host.kind != GameHostKind.TORRENT:
            return None
        link = self.host.url_for("")
        return f"{link}&so={self.file_index}" if self.file_index is not None else link

    def __repr__(self) -> str:
        return f"{self.filename} @ {self.host.name}"
