from typing import Literal

from pydantic import ConfigDict, Field, field_validator

from endpoints.responses.base import BaseModel, UTCDatetime
from models.game_comment import COMMENT_BODY_MAX_LENGTH, COMMENT_REPORT_MAX_LENGTH


class CommentAuthorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    avatar_url: str | None


class CommentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    igdb_id: int
    parent_id: int | None
    author: CommentAuthorSchema | None
    body: str
    spoiler: bool
    created_at: UTCDatetime
    updated_at: UTCDatetime
    edited: bool
    deleted: bool
    like_count: int
    reply_count: int
    liked: bool
    can_edit: bool
    can_delete: bool


class CommentPageSchema(BaseModel):
    items: list[CommentSchema]
    total: int
    limit: int
    offset: int


class CommentEditSchema(BaseModel):
    body: str = Field(min_length=1, max_length=COMMENT_BODY_MAX_LENGTH)
    spoiler: bool = False

    @field_validator("body")
    @classmethod
    def clean_body(cls, value: str) -> str:
        value = value.strip()
        if not value or any(ord(char) < 32 and char not in "\n\t\r" for char in value):
            raise ValueError("Enter a comment without control characters")
        return value


class CommentCreateSchema(CommentEditSchema):
    parent_id: int | None = Field(default=None, ge=1)


class CommentLikeSchema(BaseModel):
    liked: bool


class CommentReportCreateSchema(BaseModel):
    reason: str = Field(min_length=1, max_length=COMMENT_REPORT_MAX_LENGTH)

    @field_validator("reason")
    @classmethod
    def clean_reason(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Enter a reason")
        return value


class CommentReportActionSchema(BaseModel):
    action: Literal["dismiss", "remove"]


class CommentReportSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    comment_id: int
    game_title: str
    igdb_id: int
    reporter: CommentAuthorSchema
    author: CommentAuthorSchema | None
    reason: str
    body_snapshot: str
    status: Literal["pending", "dismissed", "removed"]
    created_at: UTCDatetime
    updated_at: UTCDatetime


class CommentReportPageSchema(BaseModel):
    items: list[CommentReportSchema]
    total: int
    limit: int
    offset: int
