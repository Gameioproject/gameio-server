from adapters.services.internet_archive import (
    fetch_item_files,
    fetch_item_metadata,
    parse_item_identifier,
)
from adapters.services.minerva import (
    fetch_torrent,
    fetch_torrent_url,
    parse_minerva_link,
    torrent_files_as_listing,
)
from handler.database import db_game_source_handler
from handler.sources.indexer import index_host_files
from handler.sources.platforms import platform_from_files, platform_from_text
from handler.sources.policy import require_server_sources
from logger.logger import log
from models.game_source import GameHostKind
from tasks.tasks import Task, TaskType, update_job_meta
from utils.context import initialize_context


class IndexGameHostTask(Task):
    def __init__(self):
        super().__init__(
            title="Index game host",
            description="List a host's files and record the ones that match catalog games as download sources",
            task_type=TaskType.SYNC,
            enabled=True,
            manual_run=True,
            cron_string=None,
        )

    @initialize_context()
    async def run(self, host_id: int) -> dict:
        require_server_sources()
        host = db_game_source_handler.get_host(host_id)
        if host is None:
            raise ValueError(f"Game host {host_id} not found")
        if host.kind == GameHostKind.TORRENT:
            return await self._run_torrent(host)
        if host.kind != GameHostKind.INTERNET_ARCHIVE:
            raise ValueError(f"Host kind {host.kind} cannot be listed")

        # Hosts created from a pasted link keep the link; the API wants the identifier.
        identifier = parse_item_identifier(host.base)
        if identifier != host.base:
            db_game_source_handler.update_host(host.id, base=identifier)
        log.info(f"Indexing {host.name} ({identifier})...")
        db_game_source_handler.mark_index_started(host.id)
        try:
            files = await fetch_item_files(identifier)
            platform_slug = host.platform_slug or await _detect_platform(
                identifier, [f["name"] for f in files]
            )
            if platform_slug and not host.platform_slug:
                db_game_source_handler.update_host(host.id, platform_slug=platform_slug)
            stats = index_host_files(host, files, default_platform=platform_slug)
        except Exception:
            db_game_source_handler.mark_index_finished(host.id, None)
            raise
        db_game_source_handler.mark_index_finished(host.id, stats.to_dict())
        update_job_meta({"index_stats": stats.to_dict()})
        log.info(
            f"Indexed {host.name}: {stats.matched} matched, {stats.unmatched} unmatched"
        )
        return stats.to_dict()

    async def _run_torrent(self, host) -> dict:
        """A MiNERVA directory is one torrent: its file list is the listing."""
        require_server_sources()
        locator = parse_minerva_link(host.base)
        log.info(f"Indexing {host.name} ({locator.canonical})...")
        db_game_source_handler.mark_index_started(host.id)
        try:
            torrent_url = await fetch_torrent_url(locator)
            torrent = await fetch_torrent(torrent_url)
            db_game_source_handler.update_host(host.id, info_hash=torrent.info_hash)
            files = torrent_files_as_listing(torrent, locator.directory)
            platform_slug = (
                host.platform_slug
                or platform_from_text(locator.directory, torrent.name, torrent_url)
                or platform_from_files([f["name"] for f in files])
            )
            if platform_slug and not host.platform_slug:
                db_game_source_handler.update_host(host.id, platform_slug=platform_slug)
            stats = index_host_files(host, files, default_platform=platform_slug)
        except Exception:
            db_game_source_handler.mark_index_finished(host.id, None)
            raise
        result = stats.to_dict()
        # The whole torrent's size decides which torrent host serves a game first:
        # debrid services cap torrents by their total size, not by the file picked.
        result["torrent_size"] = sum(f.size for f in torrent.files)
        result["torrent_files"] = len(torrent.files)
        db_game_source_handler.mark_index_finished(host.id, result)
        update_job_meta({"index_stats": result})
        log.info(
            f"Indexed {host.name}: {stats.matched} matched, {stats.unmatched} unmatched"
        )
        return result


async def _detect_platform(identifier: str, file_names: list[str]) -> str | None:
    """Read the system off the item's title/tags, else off its file extensions."""
    try:
        meta = await fetch_item_metadata(identifier)
    except Exception as exc:
        log.warning(f"Could not read metadata of {identifier}: {exc}")
        meta = {"title": "", "description": "", "subject": []}
    return platform_from_text(
        meta["title"], " ".join(meta["subject"]), identifier, meta["description"]
    ) or platform_from_files(file_names)


index_game_host_task = IndexGameHostTask()
