"""How much room open sign-up has left.

``GAMEIO_SIGNUP_MAX_USERS`` at zero or below means no ceiling. The endpoint and
the heartbeat answer from here, so clients never offer a seat that is refused.
"""

from config import GAMEIO_SIGNUP_MAX_USERS
from handler.database import db_user_handler

SIGNUP_RATE_WINDOW_SECONDS = 3600
UNLIMITED_SEATS = -1


def signup_is_capped() -> bool:
    return GAMEIO_SIGNUP_MAX_USERS > 0


def signup_seats_left() -> int:
    """Seats still open, or ``UNLIMITED_SEATS`` when the cap is off."""
    if not signup_is_capped():
        return UNLIMITED_SEATS
    return max(0, GAMEIO_SIGNUP_MAX_USERS - db_user_handler.count_users())


def signup_is_open() -> bool:
    return not signup_is_capped() or signup_seats_left() > 0
