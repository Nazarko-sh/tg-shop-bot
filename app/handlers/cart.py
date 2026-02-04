from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.keyboards import kb_cart, kb_menu
from app.i18n import t
from app.ui import send_or_edit
from app.db import Database
from app.config import Config

router = Router()


def cart_total(cart_items):
    return sum(it["qty"] * it["price_cents"] for it in cart_items)


async def show_cart(callback: CallbackQuery, db: Database, cfg: Config):
    await db.ensure_user(callback.from_user.id)
    lang = await db.get_user_lang(callback.from_user.id)

    cart = await db.get_cart(callback.from_user.id)
    if not cart:
        await send_or_edit(
            callback.bot,
            db,
            callback.message.chat.id,
            callback.from_user.id,
            t(lang, "cart_empty"),
            kb_menu(lang, int(callback.from_user.id) == int(cfg.admin_id)),
        )
        return

    total = cart_total(cart)
    lines = [t(lang, "cart_title"), ""]
    for it in cart:
        price = it["price_cents"] / 100.0
        line = (it["qty"] * it["price_cents"]) / 100.0
        lines.append(f"• {it['title']} — {it['qty']} × {price:.2f} = {line:.2f}")
    lines.append("")
    lines.append(f"💳 Total: {total/100.0:.2f}")

    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "\n".join(lines), kb_cart(lang, cart))


@router.callback_query(F.data.startswith("cart:add:"))
async def cb_cart_add(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)

    pid = int(callback.data.split(":")[2])
    p = await db.get_product(pid)
    if not p or p["is_active"] != 1:
        await show_cart(callback, db, cfg)
        return

    current = await db.cart_get_qty(callback.from_user.id, pid)
    if current + 1 > p["stock"]:
        cart = await db.get_cart(callback.from_user.id)
        if cart:
            total = cart_total(cart)
            lines = [t(lang, "stock_not_enough"), "", t(lang, "cart_title"), ""]
            for it in cart:
                lines.append(f"• {it['title']} — {it['qty']} шт.")
            lines.append("")
            lines.append(f"💳 Total: {total/100.0:.2f}")
            await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "\n".join(lines), kb_cart(lang, cart))
        else:
            await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "stock_not_enough"), None)
        return

    await db.cart_set_qty(callback.from_user.id, pid, current + 1)
    await show_cart(callback, db, cfg)


@router.callback_query(F.data.startswith("cart:rem:"))
async def cb_cart_rem(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    pid = int(callback.data.split(":")[2])
    current = await db.cart_get_qty(callback.from_user.id, pid)
    await db.cart_set_qty(callback.from_user.id, pid, current - 1)
    await show_cart(callback, db, cfg)


@router.callback_query(F.data == "cart:clear")
async def cb_cart_clear(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    await db.cart_clear(callback.from_user.id)
    await show_cart(callback, db, cfg)

