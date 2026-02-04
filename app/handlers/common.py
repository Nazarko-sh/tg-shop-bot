from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from app.keyboards import kb_language, kb_menu
from app.i18n import t
from app.ui import send_or_edit
from app.db import Database
from app.config import Config

router = Router()


def is_admin(cfg: Config, user_id: int) -> bool:
    return int(user_id) == int(cfg.admin_id)


@router.message(CommandStart())
async def cmd_start(message: Message, db: Database, cfg: Config):
    await db.ensure_user(message.from_user.id)
    lang = await db.get_user_lang(message.from_user.id)

    await send_or_edit(
        bot=message.bot,
        db=db,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        text=t(lang, "choose_language"),
        keyboard=kb_language(),
    )


@router.message(Command("admin"))
async def cmd_admin(message: Message, db: Database, cfg: Config):
    await db.ensure_user(message.from_user.id)
    lang = await db.get_user_lang(message.from_user.id)

    if not is_admin(cfg, message.from_user.id):
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "admin_only"), None)
        return

    from app.handlers.admin import show_admin_panel
    await show_admin_panel(message.bot, db, cfg, message.chat.id, message.from_user.id, lang)


@router.callback_query(F.data.startswith("lang:"))
async def cb_set_lang(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    await db.ensure_user(callback.from_user.id)

    lang = callback.data.split(":", 1)[1].strip()
    await db.set_user_lang(callback.from_user.id, lang)
    lang = await db.get_user_lang(callback.from_user.id)

    await send_or_edit(
        bot=callback.bot,
        db=db,
        chat_id=callback.message.chat.id,
        user_id=callback.from_user.id,
        text=t(lang, "language_set"),
        keyboard=kb_menu(lang, is_admin(cfg, callback.from_user.id)),
    )


@router.callback_query(F.data == "menu:language")
async def cb_language(callback: CallbackQuery, db: Database):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "choose_language"), kb_language())


@router.callback_query(F.data.in_({"nav:menu", "menu:catalog", "menu:cart", "menu:orders", "menu:support", "menu:admin"}))
async def cb_menu_nav(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    await db.ensure_user(callback.from_user.id)
    lang = await db.get_user_lang(callback.from_user.id)

    if callback.data == "nav:menu":
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "menu_title"), kb_menu(lang, is_admin(cfg, callback.from_user.id)))
        return

    if callback.data == "menu:catalog":
        from app.handlers.catalog import show_catalog
        await show_catalog(callback, db)
        return

    if callback.data == "menu:cart":
        from app.handlers.cart import show_cart
        await show_cart(callback, db, cfg)
        return

    if callback.data == "menu:orders":
        from app.handlers.orders import show_orders
        await show_orders(callback, db)
        return

    if callback.data == "menu:support":
        from app.handlers.support import show_support
        await show_support(callback, db, cfg)
        return

    if callback.data == "menu:admin":
        if not is_admin(cfg, callback.from_user.id):
            await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "admin_only"), kb_menu(lang, False))
            return
        from app.handlers.admin import show_admin_panel
        await show_admin_panel(callback.bot, db, cfg, callback.message.chat.id, callback.from_user.id, lang)
        return


@router.callback_query(F.data == "nav:catalog")
async def nav_catalog(callback: CallbackQuery, db: Database):
    await callback.answer()
    from app.handlers.catalog import show_catalog
    await show_catalog(callback, db)


@router.callback_query(F.data == "nav:cart")
async def nav_cart(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    from app.handlers.cart import show_cart
    await show_cart(callback, db, cfg)


@router.callback_query(F.data == "nav:orders")
async def nav_orders(callback: CallbackQuery, db: Database):
    await callback.answer()
    from app.handlers.orders import show_orders
    await show_orders(callback, db)


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery):
    await callback.answer()
