import logging
from aiogram import Dispatcher
from aiogram.types import ErrorEvent

logger = logging.getLogger("app.errors")


def setup_global_error_handler(dp: Dispatcher) -> None:
    @dp.errors()
    async def on_error(event: ErrorEvent):
        # Never crash polling; log full context
        try:
            logger.exception("Unhandled error: %r", event.exception)
        except Exception:
            logger.exception("Unhandled error (logging failed)")
        return True
