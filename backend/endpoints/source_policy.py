from fastapi import HTTPException, status

from handler.sources.policy import server_sources_enabled


def require_server_sources() -> None:
    if not server_sources_enabled():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Source handling moved to client add-ons",
        )
