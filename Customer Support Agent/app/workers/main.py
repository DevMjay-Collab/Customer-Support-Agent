import asyncio

import structlog

from app.config import get_settings
from app.logging import configure_logging


async def run() -> None:
    """Foundation process; domain-owned jobs arrive in their respective phases."""
    settings = get_settings()
    configure_logging(settings.log_level)
    structlog.get_logger(__name__).info("worker.started", environment=settings.app_env)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(run())

