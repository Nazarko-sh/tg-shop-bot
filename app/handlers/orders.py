from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.i18n import t
from app.keyboards import kb_back_menu, kb_order_details, kb_payment_details
from app.ui import send_or_edit
from app.db import Database
from app.config import Config

router = Router()


async def show_orders(callback: CallbackQuery, db: Database):
    await db.ensure_user(callback.from_user.id)
    lang = await db.get_user_lang(callback.from_user.id)

    orders = await db.list_user_orders(callback.from_user.id, limit=10)
    if not orders:
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "no_orders"), kb_back_menu(lang))
        return

    lines = [t(lang, "orders_title"), ""]
    for o in orders:
        lines.append(f"• #{o['id']} — {o['status']} — {o['total_cents']/100:.2f} — {o['created_at']}")
    lines.append("")
    lines.append("👇 Open any order:" if lang == "en" else "👇 Відкрий замовлення:")

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    b = InlineKeyboardBuilder()
    for o in orders:
        b.button(text=f"#{o['id']} • {o['status']}", callback_data=f"order:{o['id']}")
    b.button(text=t(lang, "menu"), callback_data="nav:menu")
    b.adjust(1)

    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "\n".join(lines), b.as_markup())


@router.callback_query(F.data.startswith("order:"))
async def cb_order_details(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)

    order_id = int(callback.data.split(":")[1])
    order = await db.get_order(order_id)
    if not order or order["user_id"] != callback.from_user.id:
        await show_orders(callback, db)
        return

    items = await db.get_order_items(order_id)
    lines = [f"📦 Order #{order_id}", ""]
    lines.append(f"{t(lang,'order_status')}: {order['status']}")
    lines.append(f"{t(lang,'created_at')}: {order['created_at']}")
    lines.append("")
    lines.append("Items:" if lang == "en" else "Товари:")
    for it in items:
        lines.append(f"• {it['title']} — {it['qty']} × {it['price_cents']/100:.2f} = {it['line_total_cents']/100:.2f}")
    lines.append("")
    lines.append(f"💳 Total: {order['total_cents']/100:.2f}")

    is_manual = (order.get("payment_method") == "MANUAL")
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "\n".join(lines), kb_order_details(lang, order_id, is_manual))


@router.callback_query(F.data.startswith("paydetails:"))
async def cb_payment_details(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)

    order_id = int(callback.data.split(":")[1])
    order = await db.get_order(order_id)
    if not order or order["user_id"] != callback.from_user.id:
        await show_orders(callback, db)
        return

    details = cfg.manual_payment_details.format(order_id=order_id)
    text = f"{t(lang,'payment_details')}\n\n{details}"
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, text, kb_payment_details(lang, order_id))
