import ipaddress

import yarl

import config


def is_shareable_host(host: str) -> bool:
    """Whether a host resolves to something other than the instance itself."""
    if host.lower() == "localhost":
        return False
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return True  # A hostname, so assume it resolves for everyone.
    return not address.is_loopback and not address.is_unspecified


def get_public_base_url() -> str | None:
    """Return ROMM_BASE_URL when it points somewhere shareable, else None."""
    url = yarl.URL(config.ROMM_BASE_URL)
    if url.scheme not in ("http", "https") or not url.host:
        return None
    if not is_shareable_host(url.host):
        return None
    return str(url).rstrip("/")


def get_support_url() -> str | None:
    """Return the configured hosted support page without exposing credentials."""
    if not config.GAMEIO_SUPPORT_URL:
        return None
    try:
        url = yarl.URL(config.GAMEIO_SUPPORT_URL)
        if (
            url.scheme != "https"
            or not url.host
            or url.user is not None
            or url.password is not None
            or not is_shareable_host(url.host)
        ):
            return None
        return str(url)
    except ValueError:
        return None
