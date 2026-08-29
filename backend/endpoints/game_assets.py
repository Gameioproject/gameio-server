from typing import Annotated

from fastapi import File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import Response

from decorators.auth import protected_route
from endpoints.responses.game_activity import GameAssetSchema
from handler.auth.constants import Scope
from handler.database import db_game_activity_handler
from models.game_activity import (
    ASSET_FILE_NAME_MAX_LENGTH,
    EMULATOR_MAX_LENGTH,
    GameAssetKind,
)
from utils.router import APIRouter

router = APIRouter(
    tags=["game assets"],
)

ASSET_FILE = File(description="The save file or state")
ASSET_SCREENSHOT = File(default=None, description="Optional thumbnail")
MAX_ASSET_BYTES = 64 * 1024 * 1024


def _game_id(igdb_id: int) -> int:
    game_id = db_game_activity_handler.game_id_for_igdb(igdb_id)
    if game_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog game with IGDB id {igdb_id} not found",
        )
    return game_id


def _own_asset(request: Request, asset_id: int):
    asset = db_game_activity_handler.get_asset(asset_id)
    if asset is None or asset.user_id != request.user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset {asset_id} not found"
        )
    return asset


@protected_route(router.get, "/catalog/{igdb_id}/assets", [Scope.ASSETS_READ])
def list_game_assets(
    request: Request,
    igdb_id: int,
    kind: Annotated[GameAssetKind | None, Query()] = None,
    emulator: Annotated[str | None, Query(max_length=EMULATOR_MAX_LENGTH)] = None,
) -> list[GameAssetSchema]:
    """The user's saves and states for a game, newest first."""
    assets = db_game_activity_handler.list_assets(
        user_id=request.user.id,
        catalog_game_id=_game_id(igdb_id),
        kind=kind,
        emulator=emulator,
    )
    return [GameAssetSchema.from_asset(a) for a in assets]


@protected_route(router.post, "/catalog/{igdb_id}/assets", [Scope.ASSETS_WRITE])
async def upload_game_asset(
    request: Request,
    igdb_id: int,
    kind: Annotated[GameAssetKind, Form()],
    file: UploadFile = ASSET_FILE,
    emulator: Annotated[str, Form(max_length=EMULATOR_MAX_LENGTH)] = "",
    file_name: Annotated[
        str | None, Form(max_length=ASSET_FILE_NAME_MAX_LENGTH)
    ] = None,
    screenshot: UploadFile | None = ASSET_SCREENSHOT,
) -> GameAssetSchema:
    """Store or replace a save/state; the same name for the same core overwrites."""
    game_id = _game_id(igdb_id)
    content = await file.read(MAX_ASSET_BYTES + 1)
    if len(content) > MAX_ASSET_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Asset is too large",
        )
    shot = await screenshot.read() if screenshot is not None else None
    asset = db_game_activity_handler.upsert_asset(
        user_id=request.user.id,
        catalog_game_id=game_id,
        kind=kind,
        emulator=emulator,
        file_name=(file_name or file.filename or kind.value)[
            :ASSET_FILE_NAME_MAX_LENGTH
        ],
        content=content,
        screenshot=shot,
    )
    return GameAssetSchema.from_asset(asset)


@protected_route(
    router.get,
    "/assets/{asset_id}/content",
    [Scope.ASSETS_READ],
    responses={status.HTTP_404_NOT_FOUND: {}},
)
def get_game_asset_content(request: Request, asset_id: int) -> Response:
    asset = _own_asset(request, asset_id)
    return Response(
        content=asset.content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{asset.file_name}"'},
    )


@protected_route(
    router.get,
    "/assets/{asset_id}/screenshot",
    [Scope.ASSETS_READ],
    responses={status.HTTP_404_NOT_FOUND: {}},
)
def get_game_asset_screenshot(request: Request, asset_id: int) -> Response:
    asset = _own_asset(request, asset_id)
    if asset.screenshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No screenshot"
        )
    return Response(content=asset.screenshot, media_type="image/png")


@protected_route(
    router.delete,
    "/assets/{asset_id}",
    [Scope.ASSETS_WRITE],
    responses={status.HTTP_404_NOT_FOUND: {}},
)
def delete_game_asset(request: Request, asset_id: int) -> None:
    if not db_game_activity_handler.delete_asset(asset_id, request.user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset {asset_id} not found"
        )
