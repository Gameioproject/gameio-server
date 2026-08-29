"""Startup script to run tasks before the main application is started."""

import asyncio

import sentry_sdk
from opentelemetry import trace

from config import SENTRY_DSN
from logger.logger import log
from utils import get_version
from utils.context import initialize_context

tracer = trace.get_tracer(__name__)


@tracer.start_as_current_span("main")
async def main() -> None:
    """Run startup tasks. Nothing is scheduled: hosts are indexed on demand."""
    async with initialize_context():
        log.info("Startup tasks completed")


if __name__ == "__main__":
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        release=f"romm@{get_version()}",
    )
    asyncio.run(main())
