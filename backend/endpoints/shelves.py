"""Curated shelf definitions for the launcher's Home.

Each shelf is a title plus parameters into the generic /api/roms browse query.
The launcher renders whatever this list serves, so shelves are curated here
without an app release. Also serves /api/roms/random for the Surprise Me
action: one well-rated game drawn from the whole catalog.
"""

from typing import Annotated, Any

from fastapi import HTTPException, Query, Request, status
from decorators.auth import protected_route
from handler.auth.constants import Scope
from handler.compat.argosy import legacy_rom
from handler.database import db_catalog_handler
from handler.database.catalog_handler import CatalogOrderBy, CatalogOrderDir
from utils.router import APIRouter

router = APIRouter(tags=["shelves"])

SHELVES: list[dict[str, Any]] = [
    {
        "key": "top-rated",
        "title": "Top rated",
        # Drawn at random from everything well rated, so the row differs each
        # time Home is opened. The client caps the row; the server does not page
        # a random order, because offsets into a reshuffled set repeat games.
        "params": {"min_rating": 85, "order_by": "random"},
    },
]


@protected_route(router.get, "/shelves", [Scope.ROMS_READ])
def get_shelves(request: Request) -> list[dict[str, Any]]:
    """The Home shelves, in display order."""
    return SHELVES


@protected_route(router.get, "/roms/random", [Scope.ROMS_READ])
def get_random_rom(
    request: Request,
    min_rating: Annotated[float, Query(ge=0, le=100)] = 75,
) -> dict[str, Any]:
    """One well-rated game from anywhere in the catalog, for Surprise Me."""
    game = db_catalog_handler.get_random_game(min_rating)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Catalog is empty"
        )
    match = db_catalog_handler.get_game(game.id)
    slugs = sorted(p.platform_slug for p in game.platforms)
    if match is None or not slugs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game has no platform"
        )
    rom = legacy_rom(match["game"], slugs[0], match["sources"])
    if rom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unmappable")
    return rom
