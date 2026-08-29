from fastapi import HTTPException, Request, status

from decorators.auth import protected_route
from endpoints.responses.game_activity import (
    PlaySessionSchema,
    PlaySessionStartSchema,
)
from handler.auth.constants import Scope
from handler.database import db_game_activity_handler
from utils.router import APIRouter

router = APIRouter(
    prefix="/play",
    tags=["play"],
)


def _own_session(request: Request, session_id: int):
    play = db_game_activity_handler.get_session(session_id)
    if play is None or play.user_id != request.user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Play session {session_id} not found",
        )
    return play


@protected_route(router.post, "/sessions", [Scope.ROMS_USER_WRITE])
def start_play_session(
    request: Request, body: PlaySessionStartSchema
) -> PlaySessionSchema:
    """Any client reports a sitting so every device sees the same recent games."""
    game_id = db_game_activity_handler.game_id_for_igdb(body.igdb_id)
    if game_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog game with IGDB id {body.igdb_id} not found",
        )
    device_id = body.device_id or getattr(request.state, "device_id", None)
    play = db_game_activity_handler.start_session(
        user_id=request.user.id, catalog_game_id=game_id, device_id=device_id
    )
    return PlaySessionSchema.from_session(play)


@protected_route(
    router.post,
    "/sessions/{session_id}/heartbeat",
    [Scope.ROMS_USER_WRITE],
    responses={status.HTTP_404_NOT_FOUND: {}},
)
def heartbeat_play_session(request: Request, session_id: int) -> PlaySessionSchema:
    _own_session(request, session_id)
    play = db_game_activity_handler.touch_session(session_id)
    assert play is not None
    return PlaySessionSchema.from_session(play)


@protected_route(
    router.post,
    "/sessions/{session_id}/stop",
    [Scope.ROMS_USER_WRITE],
    responses={status.HTTP_404_NOT_FOUND: {}},
)
def stop_play_session(request: Request, session_id: int) -> PlaySessionSchema:
    _own_session(request, session_id)
    play = db_game_activity_handler.touch_session(session_id, end=True)
    assert play is not None
    return PlaySessionSchema.from_session(play)
