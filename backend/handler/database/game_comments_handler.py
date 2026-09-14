from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, exists, func, or_, select, update
from sqlalchemy.orm import Session, aliased

from decorators.database import begin_session
from models.base import utc_now
from models.catalog import CatalogGame
from models.game_comment import (
    GameComment,
    GameCommentBlock,
    GameCommentLike,
    GameCommentReport,
)
from models.user import User

from .base_handler import DBBaseHandler


@dataclass(frozen=True)
class CommentAuthor:
    id: int
    username: str
    avatar_url: str | None


@dataclass(frozen=True)
class CommentView:
    id: int
    igdb_id: int
    parent_id: int | None
    author: CommentAuthor | None
    body: str
    spoiler: bool
    created_at: datetime
    updated_at: datetime
    edited: bool
    deleted: bool
    like_count: int
    reply_count: int
    liked: bool
    can_edit: bool
    can_delete: bool


def _author(user: User | None) -> CommentAuthor | None:
    if user is None:
        return None
    return CommentAuthor(
        user.id,
        user.username,
        f"/api/users/{user.id}/avatar" if user.avatar_path else None,
    )


def _not_blocked(user_id: int, author_id):
    return ~exists().where(
        or_(
            and_(
                GameCommentBlock.user_id == user_id,
                GameCommentBlock.blocked_user_id == author_id,
            ),
            and_(
                GameCommentBlock.blocked_user_id == user_id,
                GameCommentBlock.user_id == author_id,
            ),
        )
    )


def _reply_count(user_id: int):
    child = aliased(GameComment)
    return (
        select(func.count(child.id))
        .where(
            child.parent_id == GameComment.id,
            child.deleted_at.is_(None),
            _not_blocked(user_id, child.user_id),
        )
        .correlate(GameComment)
        .scalar_subquery()
    )


def _visible(user_id: int):
    return and_(
        _not_blocked(user_id, GameComment.user_id),
        or_(
            GameComment.deleted_at.is_(None),
            and_(GameComment.parent_id.is_(None), _reply_count(user_id) > 0),
        ),
    )


def _missing() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
    )


class DBGameCommentsHandler(DBBaseHandler):
    def _game_id(self, session: Session, igdb_id: int) -> int:
        game_id = session.scalar(
            select(CatalogGame.id).where(CatalogGame.igdb_id == igdb_id)
        )
        if game_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Catalog game not found"
            )
        return game_id

    def _comment(
        self,
        session: Session,
        comment_id: int,
        user_id: int,
        *,
        allow_deleted: bool = False,
        lock: bool = False,
    ) -> GameComment:
        query = select(GameComment).where(
            GameComment.id == comment_id, _not_blocked(user_id, GameComment.user_id)
        )
        comment = session.scalar(query.with_for_update() if lock else query)
        if comment is None or (comment.deleted_at is not None and not allow_deleted):
            raise _missing()
        if comment.parent_id is not None:
            self._comment(session, comment.parent_id, user_id, allow_deleted=True)
        return comment

    def _rows(
        self, session: Session, query, user_id: int, is_admin: bool
    ) -> list[CommentView]:
        likes = (
            select(func.count())
            .where(GameCommentLike.comment_id == GameComment.id)
            .correlate(GameComment)
            .scalar_subquery()
        )
        liked = exists().where(
            GameCommentLike.comment_id == GameComment.id,
            GameCommentLike.user_id == user_id,
        )
        rows = session.execute(
            query.add_columns(
                CatalogGame.igdb_id, User, likes, liked, _reply_count(user_id)
            )
            .join(CatalogGame, CatalogGame.id == GameComment.catalog_game_id)
            .outerjoin(User, User.id == GameComment.user_id)
        ).all()
        return [
            CommentView(
                id=comment.id,
                igdb_id=igdb_id,
                parent_id=comment.parent_id,
                author=_author(author) if comment.deleted_at is None else None,
                body=comment.body if comment.deleted_at is None else "",
                spoiler=comment.spoiler if comment.deleted_at is None else False,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                edited=comment.edited_at is not None,
                deleted=comment.deleted_at is not None,
                like_count=like_count if comment.deleted_at is None else 0,
                reply_count=reply_count,
                liked=bool(has_liked) and comment.deleted_at is None,
                can_edit=comment.user_id == user_id and comment.deleted_at is None,
                can_delete=(comment.user_id == user_id or is_admin)
                and comment.deleted_at is None,
            )
            for comment, igdb_id, author, like_count, has_liked, reply_count in rows
        ]

    @begin_session
    def list_comments(
        self,
        *,
        igdb_id: int,
        user_id: int,
        is_admin: bool,
        sort: Literal["top", "newest"],
        limit: int,
        offset: int,
        session: Session = None,  # type: ignore
    ) -> tuple[list[CommentView], int]:
        game_id = self._game_id(session, igdb_id)
        condition = and_(
            GameComment.catalog_game_id == game_id,
            GameComment.parent_id.is_(None),
            _visible(user_id),
        )
        query = select(GameComment).where(condition)
        if sort == "top":
            likes = (
                select(func.count())
                .where(GameCommentLike.comment_id == GameComment.id)
                .correlate(GameComment)
                .scalar_subquery()
            )
            query = query.order_by(likes.desc())
        query = (
            query.order_by(GameComment.created_at.desc(), GameComment.id.desc())
            .limit(limit)
            .offset(offset)
        )
        total = (
            session.scalar(
                select(func.count()).select_from(GameComment).where(condition)
            )
            or 0
        )
        return self._rows(session, query, user_id, is_admin), total

    @begin_session
    def list_replies(
        self,
        *,
        comment_id: int,
        user_id: int,
        is_admin: bool,
        limit: int,
        offset: int,
        session: Session = None,  # type: ignore
    ) -> tuple[list[CommentView], int]:
        parent = self._comment(session, comment_id, user_id, allow_deleted=True)
        parent_id = parent.parent_id or parent.id
        condition = and_(
            GameComment.parent_id == parent_id,
            GameComment.deleted_at.is_(None),
            _not_blocked(user_id, GameComment.user_id),
        )
        query = (
            select(GameComment)
            .where(condition)
            .order_by(GameComment.created_at, GameComment.id)
            .limit(limit)
            .offset(offset)
        )
        total = (
            session.scalar(
                select(func.count()).select_from(GameComment).where(condition)
            )
            or 0
        )
        return self._rows(session, query, user_id, is_admin), total

    @begin_session
    def create_comment(
        self,
        *,
        igdb_id: int,
        user_id: int,
        body: str,
        spoiler: bool,
        parent_id: int | None,
        session: Session = None,  # type: ignore
    ) -> CommentView:
        game_id = self._game_id(session, igdb_id)
        if parent_id is not None:
            parent = self._comment(session, parent_id, user_id)
            if parent.catalog_game_id != game_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reply must belong to this game",
                )
            parent_id = parent.parent_id or parent.id
            self._comment(session, parent_id, user_id)
        comment = GameComment(
            catalog_game_id=game_id,
            user_id=user_id,
            body=body,
            spoiler=spoiler,
            parent_id=parent_id,
        )
        session.add(comment)
        session.flush()
        return self._rows(
            session,
            select(GameComment).where(GameComment.id == comment.id),
            user_id,
            False,
        )[0]

    @begin_session
    def edit_comment(
        self,
        *,
        comment_id: int,
        user_id: int,
        body: str,
        spoiler: bool,
        session: Session = None,  # type: ignore
    ) -> CommentView:
        comment = self._comment(session, comment_id, user_id, lock=True)
        if comment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own comments",
            )
        comment.body, comment.spoiler, comment.edited_at = body, spoiler, utc_now()
        session.flush()
        return self._rows(
            session,
            select(GameComment).where(GameComment.id == comment.id),
            user_id,
            False,
        )[0]

    def _remove(self, session: Session, comment: GameComment) -> None:
        comment.body, comment.spoiler, comment.deleted_at = "", False, utc_now()
        session.execute(
            delete(GameCommentLike).where(GameCommentLike.comment_id == comment.id)
        )

    @begin_session
    def delete_comment(
        self,
        *,
        comment_id: int,
        user_id: int,
        is_admin: bool,
        session: Session = None,  # type: ignore
    ) -> None:
        comment = session.get(GameComment, comment_id, with_for_update=True)
        if comment is None:
            raise _missing()
        if comment.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own comments",
            )
        if comment.deleted_at is None:
            self._remove(session, comment)

    @begin_session
    def set_like(
        self,
        *,
        comment_id: int,
        user_id: int,
        liked: bool,
        is_admin: bool,
        session: Session = None,  # type: ignore
    ) -> CommentView:
        session.execute(select(User.id).where(User.id == user_id).with_for_update())
        self._comment(session, comment_id, user_id, lock=True)
        existing = session.get(GameCommentLike, (comment_id, user_id))
        if liked and existing is None:
            session.add(GameCommentLike(comment_id=comment_id, user_id=user_id))
        elif not liked and existing is not None:
            session.delete(existing)
        session.flush()
        return self._rows(
            session,
            select(GameComment).where(GameComment.id == comment_id),
            user_id,
            is_admin,
        )[0]

    @begin_session
    def report_comment(
        self,
        *,
        comment_id: int,
        user_id: int,
        reason: str,
        session: Session = None,  # type: ignore
    ) -> None:
        session.execute(select(User.id).where(User.id == user_id).with_for_update())
        comment = self._comment(session, comment_id, user_id, lock=True)
        if comment.user_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot report your own comment",
            )
        existing = session.scalar(
            select(GameCommentReport).where(
                GameCommentReport.comment_id == comment_id,
                GameCommentReport.user_id == user_id,
            )
        )
        if existing is None:
            session.add(
                GameCommentReport(
                    comment_id=comment_id,
                    user_id=user_id,
                    reason=reason,
                    body_snapshot=comment.body,
                )
            )

    @begin_session
    def list_blocks(
        self,
        *,
        user_id: int,
        session: Session = None,  # type: ignore
    ) -> list[CommentAuthor]:
        users = session.scalars(
            select(User)
            .join(GameCommentBlock, GameCommentBlock.blocked_user_id == User.id)
            .where(GameCommentBlock.user_id == user_id)
            .order_by(User.username, User.id)
        )
        return [author for user in users if (author := _author(user)) is not None]

    @begin_session
    def set_block(
        self,
        *,
        user_id: int,
        blocked_user_id: int,
        blocked: bool,
        session: Session = None,  # type: ignore
    ) -> None:
        if user_id == blocked_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot block yourself",
            )
        session.execute(select(User.id).where(User.id == user_id).with_for_update())
        if session.get(User, blocked_user_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        existing = session.get(GameCommentBlock, (user_id, blocked_user_id))
        if blocked and existing is None:
            session.add(
                GameCommentBlock(user_id=user_id, blocked_user_id=blocked_user_id)
            )
        elif not blocked and existing is not None:
            session.delete(existing)

    @begin_session
    def list_reports(
        self,
        *,
        report_status: Literal["pending", "dismissed", "removed"],
        limit: int,
        offset: int,
        session: Session = None,  # type: ignore
    ) -> tuple[list[dict], int]:
        author_user = aliased(User)
        condition = GameCommentReport.status == report_status
        rows = session.execute(
            select(
                GameCommentReport,
                CatalogGame.igdb_id,
                CatalogGame.name,
                User,
                author_user,
            )
            .join(GameComment, GameComment.id == GameCommentReport.comment_id)
            .join(CatalogGame, CatalogGame.id == GameComment.catalog_game_id)
            .join(User, User.id == GameCommentReport.user_id)
            .outerjoin(author_user, author_user.id == GameComment.user_id)
            .where(condition)
            .order_by(GameCommentReport.created_at, GameCommentReport.id)
            .limit(limit)
            .offset(offset)
        ).all()
        total = (
            session.scalar(
                select(func.count()).select_from(GameCommentReport).where(condition)
            )
            or 0
        )
        return [
            {
                "id": report.id,
                "comment_id": report.comment_id,
                "igdb_id": igdb_id,
                "game_title": game_title,
                "reporter": _author(reporter),
                "author": _author(author),
                "reason": report.reason,
                "body_snapshot": report.body_snapshot,
                "status": report.status,
                "created_at": report.created_at,
                "updated_at": report.updated_at,
            }
            for report, igdb_id, game_title, reporter, author in rows
        ], total

    @begin_session
    def resolve_report(
        self,
        *,
        report_id: int,
        user_id: int,
        action: Literal["dismiss", "remove"],
        session: Session = None,  # type: ignore
    ) -> None:
        report = session.get(GameCommentReport, report_id)
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
            )
        comment = session.get(GameComment, report.comment_id, with_for_update=True)
        session.refresh(report)
        if report.status != "pending":
            return
        if action == "remove":
            if comment is not None and comment.deleted_at is None:
                self._remove(session, comment)
            session.execute(
                update(GameCommentReport)
                .where(
                    GameCommentReport.comment_id == report.comment_id,
                    GameCommentReport.status == "pending",
                )
                .values(status="removed", resolved_by=user_id, updated_at=utc_now())
            )
        else:
            report.status, report.resolved_by = "dismissed", user_id
