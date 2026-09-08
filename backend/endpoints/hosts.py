from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status

from adapters.services.internet_archive import parse_item_identifier
from adapters.services.minerva import parse_minerva_link
from config import TASK_RESULT_TTL
from decorators.auth import protected_route
from endpoints.responses.game_source import (
    GameHostCreateSchema,
    GameHostIndexSchema,
    GameHostSchema,
    GameHostUpdateSchema,
)
from handler.auth.constants import Scope
from handler.database import db_game_source_handler
from handler.redis_handler import low_prio_queue
from models.game_source import GameHostKind
from tasks.manual.index_game_host import index_game_host_task

INDEX_LOCK_MAX_AGE = timedelta(hours=1)
from utils.router import APIRouter

router = APIRouter(
    prefix="/hosts",
    tags=["hosts"],
)


def _get_host(host_id: int):
    host = db_game_source_handler.get_host(host_id)
    if host is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game host {host_id} not found",
        )
    return host


@protected_route(router.get, "", [Scope.ROMS_READ])
def get_hosts(request: Request) -> list[GameHostSchema]:
    counts = db_game_source_handler.count_sources_by_host()
    return [
        GameHostSchema.from_host(host, counts.get(host.id, 0))
        for host in db_game_source_handler.get_hosts()
    ]


@protected_route(router.post, "", [Scope.ROMS_WRITE])
def add_host(request: Request, body: GameHostCreateSchema) -> GameHostSchema:
    base = body.base.strip()
    try:
        if body.kind == GameHostKind.INTERNET_ARCHIVE:
            base = parse_item_identifier(base)
        elif body.kind == GameHostKind.TORRENT:
            base = parse_minerva_link(base).canonical
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    host = db_game_source_handler.add_host(
        name=body.name,
        kind=body.kind,
        base=base,
        platform_slug=body.platform_slug,
        enabled=body.enabled,
    )
    return GameHostSchema.from_host(host, 0)


@protected_route(
    router.patch,
    "/{host_id}",
    [Scope.ROMS_WRITE],
    responses={status.HTTP_404_NOT_FOUND: {}},
)
def update_host(
    request: Request, host_id: int, body: GameHostUpdateSchema
) -> GameHostSchema:
    _get_host(host_id)
    host = db_game_source_handler.update_host(
        host_id,
        name=body.name,
        platform_slug=body.platform_slug,
        enabled=body.enabled,
    )
    assert host is not None
    counts = db_game_source_handler.count_sources_by_host()
    return GameHostSchema.from_host(host, counts.get(host.id, 0))


@protected_route(
    router.delete,
    "/{host_id}",
    [Scope.ROMS_WRITE],
    responses={status.HTTP_404_NOT_FOUND: {}},
)
def delete_host(request: Request, host_id: int) -> None:
    """Remove a host and every source that pointed at it."""
    if not db_game_source_handler.delete_host(host_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game host {host_id} not found",
        )


@protected_route(
    router.post,
    "/{host_id}/index",
    [Scope.ROMS_WRITE],
    responses={
        status.HTTP_400_BAD_REQUEST: {},
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_409_CONFLICT: {},
    },
)
def index_host(request: Request, host_id: int) -> GameHostIndexSchema:
    """Queue a listing of the host so its files become download sources."""
    host = _get_host(host_id)
    if host.kind == GameHostKind.HTTP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hosts of kind {host.kind} cannot be listed; add sources by hand",
        )
    if host.index_started_at is not None:
        started = host.index_started_at
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - started
        if age < INDEX_LOCK_MAX_AGE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Game host {host_id} is already being indexed",
            )
        # A run this old means the worker died mid-job (the flag only clears on
        # completion), so the lock is stale and re-indexing is the recovery.
    db_game_source_handler.mark_index_started(host.id)
    job = low_prio_queue.enqueue(
        index_game_host_task.run,
        kwargs={"host_id": host.id},
        job_timeout=index_game_host_task.timeout,
        result_ttl=TASK_RESULT_TTL,
        meta={
            "task_name": index_game_host_task.title,
            "task_type": index_game_host_task.task_type.value,
        },
    )
    return GameHostIndexSchema(task_id=job.id, host_id=host.id)
