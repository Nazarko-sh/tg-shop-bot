from aiogram import Router
from aiogram.types import CallbackQuery

from app.i18n import t
from app.keyboards import kb_back_menu
from app.ui import send_or_edit
from app.db import Database
from app.config import Config

router = Router()


async def show_support(callback: CallbackQuery, db: Database, cfg: Config):
    await db.ensure_user(callback.from_user.id)
    lang = await db.get_user_lang(callback.from_user.id)

    if lang == "ua":
        text = f"{t(lang,'support_title')}\n\n👉 {cfg.support_contact}\n\nМи відповімо якнайшвидше 🙌"
    else:
        text = f"{t(lang,'support_title')}\n\n👉 {cfg.support_contact}\n\nWe’ll reply as soon as possible 🙌"

    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, text, kb_back_menu(lang))
