import uuid

from __version__ import __version__

DEV_VERSION = "5.1.0-lite"


def get_version() -> str:
    """Returns current version tag"""
    if __version__ != "<version>":
        return __version__

    # Clients gate features on the version; an unversioned build reports the API it serves.
    return DEV_VERSION


def is_valid_uuid(uuid_str: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(uuid_str, version=4)
        return True
    except ValueError:
        return False
