from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.db import Database
from app.config import Config


class DependencyMiddleware(BaseMiddleware):
    def __init__(self, db: Database, cfg: Config):
        super().__init__()
        self.db = db
        self.cfg = cfg

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["db"] = self.db
        data["cfg"] = self.cfg
        return await handler(event, data)
