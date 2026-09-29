from config import (
    DISABLE_EMULATOR_JS,
    DISABLE_LOGS_VIEWER,
    DISABLE_RUFFLE_RS,
    DISABLE_SETUP_WIZARD,
    DISABLE_USERPASS_LOGIN,
    OIDC_AUTOLOGIN,
    OIDC_ENABLED,
    OIDC_PROVIDER,
    OIDC_RP_INITIATED_LOGOUT,
    YOUTUBE_BASE_URL,
)
from endpoints.responses.heartbeat import HeartbeatResponse
from handler.database import db_user_handler
from utils.signup import signup_is_capped, signup_seats_left
from utils import get_version
from utils.router import APIRouter
from utils.urls import get_support_url

router = APIRouter(
    tags=["system"],
)


@router.get("/heartbeat")
def heartbeat() -> HeartbeatResponse:
    """Basic server configuration for the frontend. Games come from the catalog
    and hosts, so no metadata provider, filesystem or scan task is reported."""
    seats_left = signup_seats_left()
    return {
        "SYSTEM": {
            "VERSION": get_version(),
            "SHOW_SETUP_WIZARD": len(db_user_handler.get_admin_users()) == 0
            and not DISABLE_SETUP_WIZARD,
            "CATALOG_ONLY": True,
        },
        "METADATA_SOURCES": {
            "ANY_SOURCE_ENABLED": False,
            "IGDB_API_ENABLED": False,
            "SS_API_ENABLED": False,
            "SS_DEV_CREDENTIALS_SET": False,
            "MOBY_API_ENABLED": False,
            "STEAMGRIDDB_API_ENABLED": False,
            "RA_API_ENABLED": False,
            "LAUNCHBOX_API_ENABLED": False,
            "HASHEOUS_API_ENABLED": False,
            "PLAYMATCH_API_ENABLED": False,
            "TGDB_API_ENABLED": False,
            "FLASHPOINT_API_ENABLED": False,
            "HLTB_API_ENABLED": False,
            "LIBRETRO_API_ENABLED": False,
        },
        "FILESYSTEM": {
            "FS_PLATFORMS": [],
        },
        "EMULATION": {
            "DISABLE_EMULATOR_JS": DISABLE_EMULATOR_JS,
            "DISABLE_RUFFLE_RS": DISABLE_RUFFLE_RS,
        },
        "FRONTEND": {
            "DISABLE_USERPASS_LOGIN": DISABLE_USERPASS_LOGIN,
            "DISABLE_LOGS_VIEWER": DISABLE_LOGS_VIEWER,
            "YOUTUBE_BASE_URL": YOUTUBE_BASE_URL,
            "SUPPORT_URL": get_support_url(),
            "SIGNUP_OPEN": not signup_is_capped() or seats_left > 0,
            "SIGNUP_SEATS_LEFT": seats_left,
        },
        "OIDC": {
            "ENABLED": OIDC_ENABLED,
            "AUTOLOGIN": OIDC_AUTOLOGIN,
            "PROVIDER": OIDC_PROVIDER,
            "RP_INITIATED_LOGOUT": OIDC_RP_INITIATED_LOGOUT,
        },
        "TASKS": {
            "ENABLE_SCHEDULED_RESCAN": False,
            "SCHEDULED_RESCAN_CRON": "",
            "ENABLE_SCHEDULED_UPDATE_SWITCH_TITLEDB": False,
            "SCHEDULED_UPDATE_SWITCH_TITLEDB_CRON": "",
            "ENABLE_SCHEDULED_UPDATE_LAUNCHBOX_METADATA": False,
            "SCHEDULED_UPDATE_LAUNCHBOX_METADATA_CRON": "",
            "ENABLE_SCHEDULED_CONVERT_IMAGES_TO_WEBP": False,
            "SCHEDULED_CONVERT_IMAGES_TO_WEBP_CRON": "",
        },
    }
