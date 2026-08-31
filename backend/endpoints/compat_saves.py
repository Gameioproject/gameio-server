"""The classic /api/saves and /api/states protocol, served from the asset store.

Argosy's whole save pipeline (queue, conflicts, hardcore rules) speaks the
classic RomM endpoints. The catalog fork stores saves per catalog game in
game_assets instead, so this router translates: rom ids decode to catalog
games, uploads upsert assets, listings serialize assets back into the
classic wire shape the client's models expect.
"""

from typing import Annotated, Any

from fastapi import File, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import Response

from decorators.auth import protected_route
from handler.auth.constants import Scope
from handler.compat.argosy import platform_slug, rom_id, split_rom_id
from handler.database import db_catalog_handler, db_game_activity_handler
from models.game_activity import (
    ASSET_FILE_NAME_MAX_LENGTH,
    EMULATOR_MAX_LENGTH,
    GameAsset,
    GameAssetKind,
)
from pydantic import BaseModel
from utils.router import APIRouter

router = APIRouter(tags=["compat saves"])

SAVE_FILE = File(description="The save file")
STATE_FILE = File(description="The state file")
SHOT_FILE = File(default=None, description="Optional screenshot")
MAX_ASSET_BYTES = 64 * 1024 * 1024


class DeleteIdsPayload(BaseModel):
    saves: list[int] | None = None
    states: list[int] | None = None

    @property
    def ids(self) -> list[int]:
        return self.saves or self.states or []


def _own_asset(request: Request, asset_id: int, kind: GameAssetKind) -> GameAsset:
    asset = db_game_activity_handler.get_asset(asset_id)
    if asset is None or asset.user_id != request.user.id or asset.kind != kind:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset {asset_id} not found"
        )
    return asset


def _game_for_rom(value: int) -> tuple[int, str]:
    game_id, slug = split_rom_id(value)
    if slug is None or db_catalog_handler.get_game(game_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Rom {value} not found"
        )
    return game_id, slug


def _serialize(asset: GameAsset, rom: int | None = None) -> dict[str, Any]:
    slugs = sorted(p.platform_slug for p in asset.game.platforms)
    rid = rom if rom is not None else (rom_id(asset.catalog_game_id, slugs[0]) if slugs else 0)
    shot = (
        {
            "id": asset.id,
            "file_name": f"{asset.file_name}.png",
            "download_path": f"/api/assets/{asset.id}/screenshot",
            "file_size_bytes": len(asset.screenshot or b""),
        }
        if asset.screenshot is not None
        else None
    )
    return {
        "id": asset.id,
        "rom_id": rid,
        "user_id": asset.user_id,
        "emulator": asset.emulator or None,
        "file_name": asset.file_name,
        "file_size_bytes": asset.size,
        "download_path": f"/api/saves/{asset.id}/content"
        if asset.kind == GameAssetKind.SAVE
        else f"/api/states/{asset.id}/content",
        "updated_at": asset.updated_at.isoformat(),
        "created_at": asset.created_at.isoformat(),
        "slot": asset.slot,
        "content_hash": asset.content_hash,
        "screenshot": shot,
    }


def _list(request: Request, kind: GameAssetKind, rom: int | None, platform: int | None):
    if rom is not None:
        game_id, _ = _game_for_rom(rom)
        assets = db_game_activity_handler.list_assets(
            user_id=request.user.id, catalog_game_id=game_id, kind=kind, emulator=None
        )
        return [_serialize(a, rom=rom) for a in assets]
    assets = db_game_activity_handler.list_user_assets(
        user_id=request.user.id, kind=kind
    )
    slug_filter = platform_slug(platform) if platform is not None else None
    out = []
    for asset in assets:
        slugs = sorted(p.platform_slug for p in asset.game.platforms)
        if slug_filter is not None and slug_filter not in slugs:
            continue
        out.append(_serialize(asset))
    return out


async def _upload(
    request: Request,
    kind: GameAssetKind,
    rom: int,
    emulator: str | None,
    slot: str | None,
    file: UploadFile,
    screenshot: UploadFile | None,
) -> dict[str, Any]:
    game_id, _ = _game_for_rom(rom)
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
        emulator=(emulator or "")[:EMULATOR_MAX_LENGTH],
        file_name=(file.filename or kind.value)[:ASSET_FILE_NAME_MAX_LENGTH],
        content=content,
        screenshot=shot,
        slot=slot,
    )
    return _serialize(asset, rom=rom)


async def _replace(
    request: Request,
    kind: GameAssetKind,
    asset_id: int,
    slot: str | None,
    file: UploadFile,
    screenshot: UploadFile | None,
) -> dict[str, Any]:
    asset = _own_asset(request, asset_id, kind)
    content = await file.read(MAX_ASSET_BYTES + 1)
    if len(content) > MAX_ASSET_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Asset is too large",
        )
    shot = await screenshot.read() if screenshot is not None else None
    updated = db_game_activity_handler.upsert_asset(
        user_id=request.user.id,
        catalog_game_id=asset.catalog_game_id,
        kind=kind,
        emulator=asset.emulator,
        file_name=asset.file_name,
        content=content,
        screenshot=shot if shot is not None else asset.screenshot,
        slot=slot if slot is not None else asset.slot,
    )
    return _serialize(updated)


def _content(request: Request, asset_id: int, kind: GameAssetKind) -> Response:
    asset = _own_asset(request, asset_id, kind)
    return Response(
        content=asset.content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{asset.file_name}"'},
    )


def _delete_many(request: Request, ids: list[int]) -> list[int]:
    deleted: list[int] = []
    for asset_id in ids:
        if db_game_activity_handler.delete_asset(asset_id, request.user.id):
            deleted.append(asset_id)
    return deleted


@protected_route(router.get, "/saves", [Scope.ASSETS_READ])
def list_saves(
    request: Request,
    rom_id: Annotated[int | None, Query()] = None,
    platform_id: Annotated[int | None, Query()] = None,
) -> list[dict[str, Any]]:
    return _list(request, GameAssetKind.SAVE, rom_id, platform_id)


@protected_route(router.get, "/saves/{save_id}", [Scope.ASSETS_READ])
def get_save(request: Request, save_id: int) -> dict[str, Any]:
    return _serialize(_own_asset(request, save_id, GameAssetKind.SAVE))


@protected_route(router.post, "/saves", [Scope.ASSETS_WRITE])
async def upload_save(
    request: Request,
    rom_id: Annotated[int, Query()],
    emulator: Annotated[str | None, Query()] = None,
    slot: Annotated[str | None, Query()] = None,
    autocleanup: Annotated[bool, Query()] = False,
    autocleanup_limit: Annotated[int | None, Query()] = None,
    saveFile: UploadFile = SAVE_FILE,
    screenshotFile: UploadFile | None = SHOT_FILE,
) -> dict[str, Any]:
    return await _upload(
        request, GameAssetKind.SAVE, rom_id, emulator, slot, saveFile, screenshotFile
    )


@protected_route(router.put, "/saves/{save_id}", [Scope.ASSETS_WRITE])
async def update_save(
    request: Request,
    save_id: int,
    slot: Annotated[str | None, Query()] = None,
    saveFile: UploadFile = SAVE_FILE,
    screenshotFile: UploadFile | None = SHOT_FILE,
) -> dict[str, Any]:
    return await _replace(
        request, GameAssetKind.SAVE, save_id, slot, saveFile, screenshotFile
    )


@protected_route(router.post, "/saves/delete", [Scope.ASSETS_WRITE])
def delete_saves(request: Request, payload: DeleteIdsPayload) -> list[int]:
    return _delete_many(request, payload.ids)


@protected_route(router.get, "/saves/{save_id}/content", [Scope.ASSETS_READ])
def save_content(request: Request, save_id: int) -> Response:
    return _content(request, save_id, GameAssetKind.SAVE)


@protected_route(router.get, "/states", [Scope.ASSETS_READ])
def list_states(
    request: Request,
    rom_id: Annotated[int | None, Query()] = None,
    platform_id: Annotated[int | None, Query()] = None,
) -> list[dict[str, Any]]:
    return _list(request, GameAssetKind.STATE, rom_id, platform_id)


@protected_route(router.get, "/states/{state_id}", [Scope.ASSETS_READ])
def get_state(request: Request, state_id: int) -> dict[str, Any]:
    return _serialize(_own_asset(request, state_id, GameAssetKind.STATE))


@protected_route(router.post, "/states", [Scope.ASSETS_WRITE])
async def upload_state(
    request: Request,
    rom_id: Annotated[int, Query()],
    emulator: Annotated[str | None, Query()] = None,
    stateFile: UploadFile = STATE_FILE,
    screenshotFile: UploadFile | None = SHOT_FILE,
) -> dict[str, Any]:
    return await _upload(
        request, GameAssetKind.STATE, rom_id, emulator, None, stateFile, screenshotFile
    )


@protected_route(router.put, "/states/{state_id}", [Scope.ASSETS_WRITE])
async def update_state(
    request: Request,
    state_id: int,
    stateFile: UploadFile = STATE_FILE,
    screenshotFile: UploadFile | None = SHOT_FILE,
) -> dict[str, Any]:
    return await _replace(
        request, GameAssetKind.STATE, state_id, None, stateFile, screenshotFile
    )


@protected_route(router.post, "/states/delete", [Scope.ASSETS_WRITE])
def delete_states(request: Request, payload: DeleteIdsPayload) -> list[int]:
    return _delete_many(request, payload.ids)


@protected_route(router.get, "/states/{state_id}/content", [Scope.ASSETS_READ])
def state_content(request: Request, state_id: int) -> Response:
    return _content(request, state_id, GameAssetKind.STATE)
