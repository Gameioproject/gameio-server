from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field, model_validator

from models.game_source import (
    HOST_BASE_MAX_LENGTH,
    HOST_NAME_MAX_LENGTH,
    PLATFORM_SLUG_MAX_LENGTH,
    SOURCE_FILENAME_MAX_LENGTH,
    SOURCE_PATH_MAX_LENGTH,
    SOURCE_REGION_MAX_LENGTH,
    GameHost,
    GameHostKind,
    GameSource,
)

from .base import BaseModel


class GameSourceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    host_id: int
    host_name: str
    platform_slug: str
    filename: str
    size: int | None
    md5: str | None
    sha1: str | None
    region: str | None

    @classmethod
    def from_source(cls, source: GameSource) -> "GameSourceSchema":
        return cls(
            id=source.id,
            host_id=source.host_id,
            host_name=source.host.name,
            platform_slug=source.platform_slug,
            filename=source.filename,
            size=source.size,
            md5=source.md5,
            sha1=source.sha1,
            region=source.region,
        )


class GameHostSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    kind: GameHostKind
    base: str
    platform_slug: str | None
    enabled: bool
    source_count: int
    indexing: bool
    last_indexed_at: datetime | None
    last_index_stats: dict[str, Any] | None

    @classmethod
    def from_host(cls, host: GameHost, source_count: int) -> "GameHostSchema":
        return cls(
            id=host.id,
            name=host.name,
            kind=host.kind,
            base=host.base,
            platform_slug=host.platform_slug,
            enabled=host.enabled,
            source_count=source_count,
            indexing=host.index_started_at is not None,
            last_indexed_at=host.last_indexed_at,
            last_index_stats=host.last_index_stats,
        )


class GameHostCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=HOST_NAME_MAX_LENGTH)
    kind: GameHostKind
    base: str = Field(min_length=1, max_length=HOST_BASE_MAX_LENGTH)
    platform_slug: str | None = Field(default=None, max_length=PLATFORM_SLUG_MAX_LENGTH)
    enabled: bool = True


class GameHostUpdateSchema(BaseModel):
    name: str | None = Field(
        default=None, min_length=1, max_length=HOST_NAME_MAX_LENGTH
    )
    platform_slug: str | None = Field(default=None, max_length=PLATFORM_SLUG_MAX_LENGTH)
    enabled: bool | None = None


class GameSourceCreateSchema(BaseModel):
    """Either a host + relative path, or a direct URL the server maps to a host."""

    host_id: int | None = None
    path: str | None = Field(
        default=None, min_length=1, max_length=SOURCE_PATH_MAX_LENGTH
    )
    url: str | None = Field(
        default=None, min_length=1, max_length=SOURCE_PATH_MAX_LENGTH
    )
    # Defaults to the game's first platform.
    platform_slug: str | None = Field(default=None, max_length=PLATFORM_SLUG_MAX_LENGTH)
    filename: str | None = Field(default=None, max_length=SOURCE_FILENAME_MAX_LENGTH)
    size: int | None = None
    md5: str | None = Field(default=None, max_length=32)
    sha1: str | None = Field(default=None, max_length=40)
    region: str | None = Field(default=None, max_length=SOURCE_REGION_MAX_LENGTH)

    @model_validator(mode="after")
    def _one_locator(self) -> "GameSourceCreateSchema":
        if bool(self.url) == bool(self.host_id and self.path):
            raise ValueError("Provide either url, or host_id and path")
        return self


class GameHostIndexSchema(BaseModel):
    task_id: str
    host_id: int
