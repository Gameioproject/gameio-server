"""Outbound mail, over plain SMTP so any provider is a credentials change.

With no SMTP host configured the send is skipped and the caller logs the link,
which is how a self-hosted server has always worked.
"""

import smtplib
import ssl
from email.message import EmailMessage

from config import (
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SSL,
    SMTP_STARTTLS,
    SMTP_TIMEOUT_SECONDS,
    SMTP_USER,
)
from logger.logger import log


def mail_is_configured() -> bool:
    return bool(SMTP_HOST)


def send_mail(to_address: str, subject: str, body: str) -> bool:
    """Send one plain-text message, reporting whether it was accepted.

    Never raises, so the caller decides what to do when mail is unavailable.
    """
    if not mail_is_configured():
        return False

    message = EmailMessage()
    message["From"] = SMTP_FROM
    message["To"] = to_address
    message["Subject"] = subject
    message.set_content(body)

    try:
        if SMTP_SSL:
            with smtplib.SMTP_SSL(
                SMTP_HOST or "",
                SMTP_PORT,
                timeout=SMTP_TIMEOUT_SECONDS,
                context=ssl.create_default_context(),
            ) as server:
                _authenticate(server)
                server.send_message(message)
        else:
            with smtplib.SMTP(
                SMTP_HOST or "", SMTP_PORT, timeout=SMTP_TIMEOUT_SECONDS
            ) as server:
                if SMTP_STARTTLS:
                    server.starttls(context=ssl.create_default_context())
                _authenticate(server)
                server.send_message(message)
    except Exception as exc:
        log.error(f"Could not send mail to {to_address}: {exc}")
        return False

    return True


def _authenticate(server: smtplib.SMTP) -> None:
    if SMTP_USER and SMTP_PASSWORD:
        server.login(SMTP_USER, SMTP_PASSWORD)
