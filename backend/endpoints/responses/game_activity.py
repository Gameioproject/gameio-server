from pydantic import ConfigDict, Field

from models.game_activity import (
    DEVICE_ID_MAX_LENGTH,
    GameAsset,
    GameAssetKind,
    GamePlaySession,
)

from .base import BaseModel, UTCDatetime


class PlaySessionStartSchema(BaseModel):
    igdb_id: int
    device_id: str | None = Field(default=None, max_length=DEVICE_ID_MAX_LENGTH)


class PlaySessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    igdb_id: int
    device_id: str | None
    started_at: UTCDatetime
    last_activity_at: UTCDatetime
    ended_at: UTCDatetime | None
    duration_seconds: int

    @classmethod
    def from_session(cls, play: GamePlaySession) -> "PlaySessionSchema":
        return cls(
            id=play.id,
            igdb_id=play.game.igdb_id,
            device_id=play.device_id,
            started_at=play.started_at,
            last_activity_at=play.last_activity_at,
            ended_at=play.ended_at,
            duration_seconds=play.duration_seconds,
        )


class GameAssetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    igdb_id: int
    kind: GameAssetKind
    emulator: str
    file_name: str
    size: int
    has_screenshot: bool
    updated_at: UTCDatetime

    @classmethod
    def from_asset(cls, asset: GameAsset) -> "GameAssetSchema":
        return cls(
            id=asset.id,
            igdb_id=asset.game.igdb_id,
            kind=asset.kind,
            emulator=asset.emulator,
            file_name=asset.file_name,
            size=asset.size,
            has_screenshot=asset.screenshot is not None,
            updated_at=asset.updated_at,
        )
