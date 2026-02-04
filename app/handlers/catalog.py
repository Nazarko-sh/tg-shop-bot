from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.keyboards import kb_catalog_categories, kb_category_products, kb_product
from app.i18n import t
from app.ui import send_or_edit, send_or_edit_photo
from app.db import Database

router = Router()


async def show_catalog(callback: CallbackQuery, db: Database):
    await db.ensure_user(callback.from_user.id)
    lang = await db.get_user_lang(callback.from_user.id)

    cats = await db.list_categories(only_active=True)
    if not cats:
        await send_or_edit(
            bot=callback.bot,
            db=db,
            chat_id=callback.message.chat.id,
            user_id=callback.from_user.id,
            text=t(lang, "empty_catalog"),
            keyboard=kb_catalog_categories(lang, []),
        )
        return

    await send_or_edit(
        bot=callback.bot,
        db=db,
        chat_id=callback.message.chat.id,
        user_id=callback.from_user.id,
        text=t(lang, "catalog_title"),
        keyboard=kb_catalog_categories(lang, cats),
    )


@router.callback_query(F.data.startswith("cat:"))
async def cb_open_category(callback: CallbackQuery, db: Database):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)

    cat_id = int(callback.data.split(":")[1])
    products = await db.list_products(category_id=cat_id, only_active=True)

    if not products:
        await send_or_edit(
            callback.bot,
            db,
            callback.message.chat.id,
            callback.from_user.id,
            t(lang, "empty_products"),
            kb_category_products(lang, cat_id, []),
        )
        return

    await send_or_edit(
        callback.bot,
        db,
        callback.message.chat.id,
        callback.from_user.id,
        f"{t(lang, 'catalog_title')}\n\n📁 Category #{cat_id}",
        kb_category_products(lang, cat_id, products),
    )


@router.callback_query(F.data.startswith("cat_back:"))
async def cb_cat_back(callback: CallbackQuery, db: Database):
    await callback.answer()
    await show_catalog(callback, db)


@router.callback_query(F.data.startswith("prod:"))
async def cb_open_product(callback: CallbackQuery, db: Database):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)

    product_id = int(callback.data.split(":")[1])
    p = await db.get_product(product_id)
    if not p or p["is_active"] != 1:
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "empty_products"), None)
        return

    price = p["price_cents"] / 100.0
    stock = p["stock"]
    text = (
        f"{t(lang,'product')}\n\n"
        f"🧾 {p['title']}\n"
        f"{p['description']}\n\n"
        f"💰 {price:.2f}\n"
        f"📦 Stock: {stock}"
    )

    if p.get("photo_file_id"):
        await send_or_edit_photo(callback.bot, db, callback.message.chat.id, callback.from_user.id, p["photo_file_id"], text, kb_product(lang, product_id))
    else:
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, text, kb_product(lang, product_id))
