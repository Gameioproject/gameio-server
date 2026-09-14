from typing import Annotated, Literal

from fastapi import HTTPException, Query, Request, Response, status

from decorators.auth import protected_route
from endpoints.responses.game_comment import (
    CommentAuthorSchema,
    CommentCreateSchema,
    CommentEditSchema,
    CommentLikeSchema,
    CommentPageSchema,
    CommentReportActionSchema,
    CommentReportCreateSchema,
    CommentReportPageSchema,
    CommentReportSchema,
    CommentSchema,
)
from handler.auth.constants import Scope
from handler.comment_rate_limit import check_comment_rate_limit
from handler.database import db_game_comments_handler
from models.game_comment import COMMENT_PAGE_MAX_SIZE
from models.user import Role
from utils.router import APIRouter

router = APIRouter(tags=["comments"])
PageLimit = Annotated[int, Query(ge=1, le=COMMENT_PAGE_MAX_SIZE)]
PageOffset = Annotated[int, Query(ge=0)]


def _member(request: Request) -> int:
    if request.user.is_kiosk_guest:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in to join the conversation",
        )
    return request.user.id


def _admin(request: Request) -> int:
    user_id = _member(request)
    if request.user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )
    return user_id


@protected_route(router.get, "/catalog/{igdb_id}/comments", [Scope.ROMS_READ])
def list_comments(
    request: Request,
    igdb_id: int,
    sort: Literal["top", "newest"] = "top",
    limit: PageLimit = 20,
    offset: PageOffset = 0,
) -> CommentPageSchema:
    items, total = db_game_comments_handler.list_comments(
        igdb_id=igdb_id,
        user_id=request.user.id,
        is_admin=request.user.role == Role.ADMIN,
        sort=sort,
        limit=limit,
        offset=offset,
    )
    return CommentPageSchema(
        items=[CommentSchema.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@protected_route(
    router.post,
    "/catalog/{igdb_id}/comments",
    [Scope.ROMS_READ, Scope.ROMS_USER_WRITE],
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    request: Request, igdb_id: int, body: CommentCreateSchema
) -> CommentSchema:
    user_id = _member(request)
    check_comment_rate_limit(user_id, "post")
    return CommentSchema.model_validate(
        db_game_comments_handler.create_comment(
            igdb_id=igdb_id, user_id=user_id, **body.model_dump()
        )
    )


@protected_route(router.get, "/comments/blocks", [Scope.ME_READ])
def list_comment_blocks(request: Request) -> list[CommentAuthorSchema]:
    return [
        CommentAuthorSchema.model_validate(author)
        for author in db_game_comments_handler.list_blocks(user_id=_member(request))
    ]


@protected_route(
    router.put,
    "/comments/blocks/{user_id}",
    [Scope.ME_WRITE],
    status_code=status.HTTP_204_NO_CONTENT,
)
def block_comment_author(request: Request, user_id: int) -> Response:
    own_id = _member(request)
    check_comment_rate_limit(own_id, "block")
    db_game_comments_handler.set_block(
        user_id=own_id, blocked_user_id=user_id, blocked=True
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@protected_route(
    router.delete,
    "/comments/blocks/{user_id}",
    [Scope.ME_WRITE],
    status_code=status.HTTP_204_NO_CONTENT,
)
def unblock_comment_author(request: Request, user_id: int) -> Response:
    own_id = _member(request)
    check_comment_rate_limit(own_id, "block")
    db_game_comments_handler.set_block(
        user_id=own_id, blocked_user_id=user_id, blocked=False
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@protected_route(
    router.get, "/comments/reports", [Scope.ROMS_READ, Scope.ROMS_USER_WRITE]
)
def list_comment_reports(
    request: Request,
    report_status: Literal["pending", "dismissed", "removed"] = "pending",
    limit: PageLimit = 20,
    offset: PageOffset = 0,
) -> CommentReportPageSchema:
    _admin(request)
    items, total = db_game_comments_handler.list_reports(
        report_status=report_status, limit=limit, offset=offset
    )
    return CommentReportPageSchema(
        items=[CommentReportSchema.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@protected_route(
    router.patch,
    "/comments/reports/{report_id}",
    [Scope.ROMS_READ, Scope.ROMS_USER_WRITE],
    status_code=status.HTTP_204_NO_CONTENT,
)
def resolve_comment_report(
    request: Request, report_id: int, body: CommentReportActionSchema
) -> Response:
    db_game_comments_handler.resolve_report(
        report_id=report_id, user_id=_admin(request), action=body.action
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@protected_route(router.get, "/comments/{comment_id}/replies", [Scope.ROMS_READ])
def list_comment_replies(
    request: Request, comment_id: int, limit: PageLimit = 20, offset: PageOffset = 0
) -> CommentPageSchema:
    items, total = db_game_comments_handler.list_replies(
        comment_id=comment_id,
        user_id=request.user.id,
        is_admin=request.user.role == Role.ADMIN,
        limit=limit,
        offset=offset,
    )
    return CommentPageSchema(
        items=[CommentSchema.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@protected_route(
    router.patch, "/comments/{comment_id}", [Scope.ROMS_READ, Scope.ROMS_USER_WRITE]
)
def edit_comment(
    request: Request, comment_id: int, body: CommentEditSchema
) -> CommentSchema:
    user_id = _member(request)
    check_comment_rate_limit(user_id, "edit")
    return CommentSchema.model_validate(
        db_game_comments_handler.edit_comment(
            comment_id=comment_id, user_id=user_id, **body.model_dump()
        )
    )


@protected_route(
    router.delete,
    "/comments/{comment_id}",
    [Scope.ROMS_READ, Scope.ROMS_USER_WRITE],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(request: Request, comment_id: int) -> Response:
    db_game_comments_handler.delete_comment(
        comment_id=comment_id,
        user_id=_member(request),
        is_admin=request.user.role == Role.ADMIN,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@protected_route(
    router.put, "/comments/{comment_id}/like", [Scope.ROMS_READ, Scope.ROMS_USER_WRITE]
)
def like_comment(
    request: Request, comment_id: int, body: CommentLikeSchema
) -> CommentSchema:
    user_id = _member(request)
    check_comment_rate_limit(user_id, "like")
    return CommentSchema.model_validate(
        db_game_comments_handler.set_like(
            comment_id=comment_id,
            user_id=user_id,
            liked=body.liked,
            is_admin=request.user.role == Role.ADMIN,
        )
    )


@protected_route(
    router.put,
    "/comments/{comment_id}/report",
    [Scope.ROMS_READ, Scope.ROMS_USER_WRITE],
    status_code=status.HTTP_204_NO_CONTENT,
)
def report_comment(
    request: Request, comment_id: int, body: CommentReportCreateSchema
) -> Response:
    user_id = _member(request)
    check_comment_rate_limit(user_id, "report")
    db_game_comments_handler.report_comment(
        comment_id=comment_id, user_id=user_id, reason=body.reason
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
