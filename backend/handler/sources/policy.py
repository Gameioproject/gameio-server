"""Rollout policy for moving source handling from the server to client add-ons."""

import config


class SourceHandlingDisabled(RuntimeError):
    pass


def server_sources_enabled() -> bool:
    return not config.GAMEIO_CLIENT_ADDONS_ONLY


def require_server_sources() -> None:
    if not server_sources_enabled():
        raise SourceHandlingDisabled("Source handling moved to client add-ons")
