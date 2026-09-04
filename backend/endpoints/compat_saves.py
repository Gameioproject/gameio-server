"""The classic /api/saves and /api/states protocol, served from the asset store.

Argosy's whole save pipeline (queue, conflicts, hardcore rules) speaks the
classic RomM endpoints. The catalog fork stores saves per catalog game in
game_assets instead, so this router translates: rom ids decode to catalog
games, uploads upsert assets, listings serialize assets back into the
classic wire shape the client's models expect.
"""

import gzip
import zlib
from typing import Annotated, Any

from fastapi import File, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import Response

from decorators.auth import protected_route
from handler.auth.constants import Scope
from handler.compat.argosy import platform_slug, rom_id, split_rom_id, utc_iso
from handler.database import db_catalog_handler, db_game_activity_handler
from models.game_activity import (
    ASSET_FILE_NAME_MAX_LENGTH,
    CHANNEL_MAX_LENGTH,
    DEFAULT_CHANNEL,
    DEVICE_ID_MAX_LENGTH,
    EMULATOR_MAX_LENGTH,
    GameAsset,
    GameAssetKind,
    asset_unit_key,
)
from pydantic import BaseModel, Field
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
        "game_id": asset.catalog_game_id,
        "kind": asset.kind.value,
        "user_id": asset.user_id,
        "emulator": asset.emulator or None,
        "channel": asset.channel,
        "state_slot": asset.slot_number if asset.kind == GameAssetKind.STATE else None,
        "updated_by_device_id": asset.updated_by_device_id,
        "file_name": asset.file_name,
        "file_size_bytes": asset.size,
        "download_path": f"/api/saves/{asset.id}/content"
        if asset.kind == GameAssetKind.SAVE
        else f"/api/states/{asset.id}/content",
        "updated_at": utc_iso(asset.updated_at),
        "created_at": utc_iso(asset.created_at),
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


def _clean_channel(channel: str | None) -> str:
    value = (channel or "").strip()
    return value[:CHANNEL_MAX_LENGTH] if value else DEFAULT_CHANNEL


def _refuse_if_stale(
    existing: GameAsset | None,
    base_hash: str | None,
    overwrite: bool,
    rom: int | None,
) -> None:
    """The reconcile rule's write half: a client that names the version it built on
    may not replace a unit that has moved past it unless it says so."""
    if existing is None or overwrite or base_hash is None:
        return
    if existing.content_hash and existing.content_hash != base_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "stale_base", "asset": _serialize(existing, rom=rom)},
        )


GZIP_MEDIA_TYPES = frozenset({"application/gzip", "application/x-gzip"})


def _too_large() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail="Asset is too large",
    )


async def _read_parts(
    file: UploadFile, screenshot: UploadFile | None
) -> tuple[bytes, bytes | None]:
    """Read the asset bytes; a part sent as gzip is stored and hashed decompressed."""
    content = await file.read(MAX_ASSET_BYTES + 1)
    if len(content) > MAX_ASSET_BYTES:
        raise _too_large()
    if (file.content_type or "") in GZIP_MEDIA_TYPES:
        try:
            content = zlib.decompressobj(wbits=31).decompress(content, MAX_ASSET_BYTES + 1)
        except zlib.error as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Asset is not valid gzip",
            ) from exc
        if len(content) > MAX_ASSET_BYTES:
            raise _too_large()
    shot = await screenshot.read() if screenshot is not None else None
    return content, shot


async def _upload(
    request: Request,
    kind: GameAssetKind,
    rom: int,
    emulator: str | None,
    channel: str | None,
    slot_number: int,
    file: UploadFile,
    screenshot: UploadFile | None,
    base_hash: str | None = None,
    overwrite: bool = False,
    device_id: str | None = None,
) -> dict[str, Any]:
    game_id, _ = _game_for_rom(rom)
    emulator_label = (emulator or "")[:EMULATOR_MAX_LENGTH]
    channel_name = _clean_channel(channel)
    existing = db_game_activity_handler.get_unit(
        user_id=request.user.id,
        catalog_game_id=game_id,
        unit_key=asset_unit_key(kind, emulator_label, channel_name, slot_number),
    )
    _refuse_if_stale(existing, base_hash, overwrite, rom)
    content, shot = await _read_parts(file, screenshot)
    asset = db_game_activity_handler.upsert_asset(
        user_id=request.user.id,
        catalog_game_id=game_id,
        kind=kind,
        emulator=emulator_label,
        channel=channel_name,
        slot_number=slot_number,
        file_name=(file.filename or kind.value)[:ASSET_FILE_NAME_MAX_LENGTH],
        content=content,
        screenshot=shot,
        device_id=(device_id or None) and device_id[:DEVICE_ID_MAX_LENGTH],
    )
    return _serialize(asset, rom=rom)


async def _replace(
    request: Request,
    kind: GameAssetKind,
    asset_id: int,
    file: UploadFile,
    screenshot: UploadFile | None,
    base_hash: str | None = None,
    overwrite: bool = False,
    device_id: str | None = None,
) -> dict[str, Any]:
    asset = _own_asset(request, asset_id, kind)
    _refuse_if_stale(asset, base_hash, overwrite, rom=None)
    content, shot = await _read_parts(file, screenshot)
    updated = db_game_activity_handler.upsert_asset(
        user_id=request.user.id,
        catalog_game_id=asset.catalog_game_id,
        kind=kind,
        emulator=asset.emulator,
        channel=asset.channel,
        slot_number=asset.slot_number,
        file_name=(file.filename or asset.file_name)[:ASSET_FILE_NAME_MAX_LENGTH],
        content=content,
        screenshot=shot if shot is not None else asset.screenshot,
        device_id=(device_id or None) and device_id[:DEVICE_ID_MAX_LENGTH],
    )
    return _serialize(updated)


def _content(request: Request, asset_id: int, kind: GameAssetKind) -> Response:
    """Serve the bytes, gzip-encoded when the client accepts it: emulator states are mostly
    zeros and shrink to a few percent, which is the difference between seconds and minutes
    on a home uplink."""
    asset = _own_asset(request, asset_id, kind)
    headers = {
        "Content-Disposition": f'attachment; filename="{asset.file_name}"',
        "Vary": "Accept-Encoding",
    }
    body = asset.content
    if "gzip" in request.headers.get("accept-encoding", ""):
        body = gzip.compress(body, compresslevel=1)
        headers["Content-Encoding"] = "gzip"
    return Response(content=body, media_type="application/octet-stream", headers=headers)


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
    channel: Annotated[str | None, Query()] = None,
    # Classic clients name the channel "slot"; the two are the same thing here.
    slot: Annotated[str | None, Query()] = None,
    base_hash: Annotated[str | None, Query()] = None,
    overwrite: Annotated[bool, Query()] = False,
    device_id: Annotated[str | None, Query()] = None,
    autocleanup: Annotated[bool, Query()] = False,
    autocleanup_limit: Annotated[int | None, Query()] = None,
    saveFile: UploadFile = SAVE_FILE,
    screenshotFile: UploadFile | None = SHOT_FILE,
) -> dict[str, Any]:
    return await _upload(
        request, GameAssetKind.SAVE, rom_id, emulator, channel or slot, 0,
        saveFile, screenshotFile, base_hash, overwrite, device_id,
    )


@protected_route(router.put, "/saves/{save_id}", [Scope.ASSETS_WRITE])
async def update_save(
    request: Request,
    save_id: int,
    slot: Annotated[str | None, Query()] = None,
    base_hash: Annotated[str | None, Query()] = None,
    overwrite: Annotated[bool, Query()] = False,
    device_id: Annotated[str | None, Query()] = None,
    saveFile: UploadFile = SAVE_FILE,
    screenshotFile: UploadFile | None = SHOT_FILE,
) -> dict[str, Any]:
    return await _replace(
        request, GameAssetKind.SAVE, save_id, saveFile, screenshotFile,
        base_hash, overwrite, device_id,
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
    channel: Annotated[str | None, Query()] = None,
    slot: Annotated[int, Query()] = 0,
    base_hash: Annotated[str | None, Query()] = None,
    overwrite: Annotated[bool, Query()] = False,
    device_id: Annotated[str | None, Query()] = None,
    stateFile: UploadFile = STATE_FILE,
    screenshotFile: UploadFile | None = SHOT_FILE,
) -> dict[str, Any]:
    return await _upload(
        request, GameAssetKind.STATE, rom_id, emulator, channel, slot,
        stateFile, screenshotFile, base_hash, overwrite, device_id,
    )


@protected_route(router.put, "/states/{state_id}", [Scope.ASSETS_WRITE])
async def update_state(
    request: Request,
    state_id: int,
    base_hash: Annotated[str | None, Query()] = None,
    overwrite: Annotated[bool, Query()] = False,
    device_id: Annotated[str | None, Query()] = None,
    stateFile: UploadFile = STATE_FILE,
    screenshotFile: UploadFile | None = SHOT_FILE,
) -> dict[str, Any]:
    return await _replace(
        request, GameAssetKind.STATE, state_id, stateFile, screenshotFile,
        base_hash, overwrite, device_id,
    )


@protected_route(router.post, "/states/delete", [Scope.ASSETS_WRITE])
def delete_states(request: Request, payload: DeleteIdsPayload) -> list[int]:
    return _delete_many(request, payload.ids)


@protected_route(router.get, "/states/{state_id}/content", [Scope.ASSETS_READ])
def state_content(request: Request, state_id: int) -> Response:
    return _content(request, state_id, GameAssetKind.STATE)


# --- Reconcile -----------------------------------------------------------------


class ReconcileItem(BaseModel):
    rom_id: int
    kind: GameAssetKind
    emulator: str = Field(default="", max_length=EMULATOR_MAX_LENGTH)
    channel: str = Field(default=DEFAULT_CHANNEL, max_length=CHANNEL_MAX_LENGTH)
    slot: int = 0
    has_local: bool = True
    local_hash: str | None = None
    base_hash: str | None = None
    local_changed: bool = False


class ReconcilePayload(BaseModel):
    device_id: str | None = Field(default=None, max_length=DEVICE_ID_MAX_LENGTH)
    present_roms: list[int] = Field(default_factory=list)
    items: list[ReconcileItem] = Field(default_factory=list)


def _decide(item: ReconcileItem, server: GameAsset | None) -> tuple[str, str]:
    """The reconcile rule from docs/SAVE_SYNC.md; hashes only, never clocks."""
    if server is None:
        return ("upload", "not on server") if item.has_local else ("no_op", "nothing anywhere")
    if not item.has_local:
        return "download", "server only"
    if item.local_hash and item.local_hash == server.content_hash:
        return "no_op", "identical"
    if item.base_hash is None:
        return "conflict", "never synced, both sides have a version"
    if item.base_hash == server.content_hash:
        if item.local_changed:
            return "upload", "local changed, server unchanged"
        return "no_op", "unchanged since last sync"
    if item.local_changed:
        return "conflict", "both changed since last sync"
    return "download", "server changed, local unchanged"


def _operation(
    action: str,
    reason: str,
    rom: int,
    kind: GameAssetKind,
    emulator: str,
    channel: str,
    slot: int,
    server: GameAsset | None,
) -> dict[str, Any]:
    return {
        "action": action,
        "reason": reason,
        "rom_id": rom,
        "kind": kind.value,
        "emulator": emulator or None,
        "channel": channel,
        "slot": slot if kind == GameAssetKind.STATE else 0,
        "asset_id": server.id if server else None,
        "file_name": server.file_name if server else None,
        "server_hash": server.content_hash if server else None,
        "server_updated_at": utc_iso(server.updated_at) if server else None,
        "server_size": server.size if server else None,
    }


@protected_route(router.post, "/sync/reconcile", [Scope.ASSETS_READ])
def reconcile(request: Request, payload: ReconcilePayload) -> dict[str, Any]:
    """Plan the client's uploads and downloads for saves and states in one pass."""
    rom_by_game: dict[int, int] = {}
    for present in payload.present_roms:
        game_id, slug = split_rom_id(present)
        if slug is not None:
            rom_by_game.setdefault(game_id, present)
    for item in payload.items:
        game_id, slug = split_rom_id(item.rom_id)
        if slug is not None:
            rom_by_game.setdefault(game_id, item.rom_id)

    assets = db_game_activity_handler.list_assets_for_games(
        user_id=request.user.id, catalog_game_ids=list(rom_by_game)
    )
    by_unit: dict[tuple[int, str], GameAsset] = {
        (a.catalog_game_id, a.unit_key): a for a in assets
    }

    operations: list[dict[str, Any]] = []
    mentioned: set[tuple[int, str]] = set()
    for item in payload.items:
        game_id, slug = split_rom_id(item.rom_id)
        if slug is None:
            continue
        channel = _clean_channel(item.channel)
        slot = item.slot if item.kind == GameAssetKind.STATE else 0
        key = asset_unit_key(item.kind, item.emulator, channel, slot)
        mentioned.add((game_id, key))
        server = by_unit.get((game_id, key))
        action, reason = _decide(item, server)
        operations.append(
            _operation(action, reason, item.rom_id, item.kind, item.emulator, channel, slot, server)
        )

    for (game_id, key), server in by_unit.items():
        if (game_id, key) in mentioned:
            continue
        rom_id = rom_by_game.get(game_id)
        if rom_id is None:
            continue
        operations.append(
            _operation(
                "download", "server only", rom_id, server.kind, server.emulator,
                server.channel, server.slot_number, server,
            )
        )

    return {"operations": operations}
