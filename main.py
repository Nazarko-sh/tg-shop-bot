import asyncio

from aiogram import Dispatcher
from app.bot import create_bot
from app.config import load_config
from app.logger import setup_logging
from app.errors import setup_global_error_handler
from app.db import Database
from app.middlewares import DependencyMiddleware

from app.handlers.common import router as common_router
from app.handlers.catalog import router as catalog_router
from app.handlers.cart import router as cart_router
from app.handlers.checkout import router as checkout_router
from app.handlers.orders import router as orders_router
from app.handlers.support import router as support_router
from app.handlers.admin import router as admin_router


async def main():
    setup_logging()
    cfg = load_config()

    bot = create_bot(cfg.bot_token)

    db = Database(cfg.db_path)
    await db.init()

    dp = Dispatcher()
    setup_global_error_handler(dp)

    # ✅ inject db/cfg into handler kwargs
    dp.update.middleware(DependencyMiddleware(db=db, cfg=cfg))

    dp.include_router(common_router)
    dp.include_router(catalog_router)
    dp.include_router(cart_router)
    dp.include_router(checkout_router)
    dp.include_router(orders_router)
    dp.include_router(support_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
