from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.states import CheckoutStates
from app.keyboards import kb_checkout_delivery, kb_comment, kb_confirm, kb_payment, kb_menu
from app.i18n import t, delivery_label
from app.ui import send_or_edit, safe_delete_message
from app.utils import valid_min_len, valid_phone, normalize_phone
from app.db import Database
from app.config import Config

router = Router()


def cart_summary(cart):
    total = 0
    items_lines = []
    for it in cart:
        total += it["qty"] * it["price_cents"]
        items_lines.append(f"• {it['title']} — {it['qty']} шт.")
    return items_lines, total


async def checkout_start(callback: CallbackQuery, db: Database):
    await db.ensure_user(callback.from_user.id)
    lang = await db.get_user_lang(callback.from_user.id)

    cart = await db.get_cart(callback.from_user.id)
    if not cart:
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "cart_empty"), None)
        return

    await send_or_edit(
        callback.bot,
        db,
        callback.message.chat.id,
        callback.from_user.id,
        f"{t(lang,'checkout_intro')}\n\n{t(lang,'ask_name')}",
        None,
    )


async def show_confirm_screen(bot, db: Database, chat_id: int, user_id: int, state: FSMContext):
    lang = await db.get_user_lang(user_id)
    cart = await db.get_cart(user_id)
    items_lines, total = cart_summary(cart)
    data = await state.get_data()

    text = [
        t(lang, "confirm_title"),
        "",
        f"👤 Name: {data.get('name','')}",
        f"📞 Phone: {data.get('phone','')}",
        f"🏙️ City: {data.get('city','')}",
        f"🚚 Delivery: {delivery_label(lang, data.get('delivery_method',''))}",
        f"📍 Address: {data.get('address','')}",
        f"📝 Comment: {data.get('comment') or '-'}",
        "",
        "🧺 Cart:",
        *items_lines,
        "",
        f"💳 Total: {total/100.0:.2f}",
    ]

    await send_or_edit(bot, db, chat_id, user_id, "\n".join(text), kb_confirm(lang))


@router.callback_query(F.data == "cart:checkout")
async def cb_checkout_start(callback: CallbackQuery, db: Database, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(CheckoutStates.name)
    await checkout_start(callback, db)


@router.message(CheckoutStates.name)
async def st_name(message: Message, db: Database, state: FSMContext):
    await db.ensure_user(message.from_user.id)
    lang = await db.get_user_lang(message.from_user.id)

    text = (message.text or "").strip()
    await safe_delete_message(message)

    if not valid_min_len(text, 2):
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "invalid_name") + "\n\n" + t(lang, "ask_name"), None)
        return

    await state.update_data(name=text)
    await state.set_state(CheckoutStates.phone)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "ask_phone"), None)


@router.message(CheckoutStates.phone)
async def st_phone(message: Message, db: Database, state: FSMContext):
    await db.ensure_user(message.from_user.id)
    lang = await db.get_user_lang(message.from_user.id)

    text = (message.text or "").strip()
    await safe_delete_message(message)

    phone = normalize_phone(text)
    if not valid_phone(phone):
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "invalid_phone") + "\n\n" + t(lang, "ask_phone"), None)
        return

    await state.update_data(phone=phone)
    await state.set_state(CheckoutStates.city)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "ask_city"), None)


@router.message(CheckoutStates.city)
async def st_city(message: Message, db: Database, state: FSMContext):
    await db.ensure_user(message.from_user.id)
    lang = await db.get_user_lang(message.from_user.id)

    text = (message.text or "").strip()
    await safe_delete_message(message)

    if not valid_min_len(text, 2):
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "invalid_city") + "\n\n" + t(lang, "ask_city"), None)
        return

    await state.update_data(city=text)
    await state.set_state(CheckoutStates.delivery)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "ask_delivery"), kb_checkout_delivery(lang))


@router.callback_query(CheckoutStates.delivery, F.data.startswith("del:"))
async def st_delivery(callback: CallbackQuery, db: Database, state: FSMContext):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)

    code = callback.data.split(":")[1]
    await state.update_data(delivery_method=code)
    await state.set_state(CheckoutStates.address)

    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, f"{t(lang,'ask_address')}\n\n({delivery_label(lang, code)})", None)


@router.message(CheckoutStates.address)
async def st_address(message: Message, db: Database, state: FSMContext):
    await db.ensure_user(message.from_user.id)
    lang = await db.get_user_lang(message.from_user.id)

    text = (message.text or "").strip()
    await safe_delete_message(message)

    if not valid_min_len(text, 5):
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "invalid_address") + "\n\n" + t(lang, "ask_address"), None)
        return

    await state.update_data(address=text)
    await state.set_state(CheckoutStates.comment)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "ask_comment"), kb_comment(lang))


@router.callback_query(CheckoutStates.comment, F.data == "comment:skip")
async def st_comment_skip(callback: CallbackQuery, db: Database, state: FSMContext):
    await callback.answer()
    await state.update_data(comment=None)
    await show_confirm_screen(callback.bot, db, callback.message.chat.id, callback.from_user.id, state)


@router.message(CheckoutStates.comment)
async def st_comment(message: Message, db: Database, state: FSMContext):
    await db.ensure_user(message.from_user.id)
    await safe_delete_message(message)

    text = (message.text or "").strip()
    await state.update_data(comment=text if text else None)
    await show_confirm_screen(message.bot, db, message.chat.id, message.from_user.id, state)


@router.callback_query(F.data.startswith("edit:"))
async def cb_edit_field(callback: CallbackQuery, db: Database, state: FSMContext):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)

    field = callback.data.split(":")[1]

    if field == "name":
        await state.set_state(CheckoutStates.name)
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "ask_name"), None)
        return
    if field == "phone":
        await state.set_state(CheckoutStates.phone)
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "ask_phone"), None)
        return
    if field == "city":
        await state.set_state(CheckoutStates.city)
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "ask_city"), None)
        return
    if field == "delivery":
        await state.set_state(CheckoutStates.delivery)
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "ask_delivery"), kb_checkout_delivery(lang))
        return
    if field == "address":
        await state.set_state(CheckoutStates.address)
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "ask_address"), None)
        return
    if field == "comment":
        await state.set_state(CheckoutStates.comment)
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "ask_comment"), kb_comment(lang))
        return

    await show_confirm_screen(callback.bot, db, callback.message.chat.id, callback.from_user.id, state)


@router.callback_query(F.data == "order:cancel")
async def cb_order_cancel(callback: CallbackQuery, db: Database, cfg: Config, state: FSMContext):
    await callback.answer()
    await state.clear()
    lang = await db.get_user_lang(callback.from_user.id)
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "menu_title"), kb_menu(lang, int(callback.from_user.id) == int(cfg.admin_id)))


@router.callback_query(F.data == "order:confirm")
async def cb_order_confirm(callback: CallbackQuery, db: Database, cfg: Config, state: FSMContext):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)

    cart = await db.get_cart(callback.from_user.id)
    if not cart:
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "cart_empty"), kb_menu(lang, int(callback.from_user.id) == int(cfg.admin_id)))
        await state.clear()
        return

    data = await state.get_data()
    required = ["name", "phone", "city", "delivery_method", "address"]
    if not all(data.get(k) for k in required):
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "Some required fields are missing. Please edit and try again.", kb_confirm(lang))
        return

    try:
        order_id, total = await db.create_order_from_cart(
            user_id=callback.from_user.id,
            name=data["name"],
            phone=data["phone"],
            city=data["city"],
            delivery_method=data["delivery_method"],
            address=data["address"],
            comment=data.get("comment"),
        )
    except Exception:
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "Checkout failed. Please try again.", kb_menu(lang, int(callback.from_user.id) == int(cfg.admin_id)))
        return

    await state.clear()

    # notify admin (safe parse_mode none)
    try:
        items_lines, _ = cart_summary(cart)
        admin_text = (
            f"🛒 NEW ORDER #{order_id}\n\n"
            f"User: {callback.from_user.id}\n"
            f"Name: {data.get('name')}\n"
            f"Phone: {data.get('phone')}\n"
            f"City: {data.get('city')}\n"
            f"Delivery: {data.get('delivery_method')}\n"
            f"Address: {data.get('address')}\n"
            f"Comment: {data.get('comment') or '-'}\n\n"
            f"Items:\n" + "\n".join(items_lines) + "\n\n"
            f"Total: {total/100.0:.2f}\n"
        )
        from app.keyboards import kb_admin_order
        await callback.bot.send_message(chat_id=cfg.admin_id, text=admin_text, reply_markup=kb_admin_order("en", order_id))
    except Exception:
        pass

    await send_or_edit(
        callback.bot,
        db,
        callback.message.chat.id,
        callback.from_user.id,
        f"{t(lang,'order_created')}\n\n{t(lang,'payment_title')}\nOrder #{order_id}\nTotal: {total/100.0:.2f}",
        kb_payment(lang, order_id),
    )


@router.callback_query(F.data.startswith("pay:"))
async def cb_payment(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)

    _, method, order_id_s = callback.data.split(":")
    order_id = int(order_id_s)

    if method == "manual":
        await db.set_order_payment_method(order_id, "MANUAL")
        details = cfg.manual_payment_details.format(order_id=order_id)
        text = f"{t(lang,'payment_title')}\n\n🏦 {t(lang,'payment_details')}\n\n{details}"
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, text, kb_payment(lang, order_id))
        return

    if method == "online":
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "coming_soon"), kb_payment(lang, order_id))
        return
