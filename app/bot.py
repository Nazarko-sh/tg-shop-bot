from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from app.texts import START_TEXT, product_text, cart_text, order_summary_text


from app.config import load_config, Config
from app.db import DB
from app.states import Checkout
from app import keyboards as kb
from app.texts import START_TEXT, product_text, cart_text, order_summary_text


def _safe_user_label(user) -> str:
    uname = user.username
    label = user.full_name
    if uname:
        label += f" (@{uname})"
    return label


async def main():
    cfg: Config = load_config()
    db = DB(cfg.db_path)

    bot = Bot(token=cfg.bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # ---------- START / MENU ----------
    @dp.message(CommandStart())
    async def start(m: Message, state: FSMContext):
        await state.clear()
        await m.answer(START_TEXT, reply_markup=kb.main_menu_kb())

    @dp.callback_query(F.data == "menu")
    async def menu(c: CallbackQuery, state: FSMContext):
        await state.clear()
        await c.message.edit_text(START_TEXT, reply_markup=kb.main_menu_kb())
        await c.answer()

    # ---------- CATALOG ----------
    @dp.callback_query(F.data == "catalog")
    async def catalog(c: CallbackQuery):
        categories = db.get_categories()
        await c.message.edit_text("🗂️ <b>Categories:</b>", reply_markup=kb.categories_kb(categories))
        await c.answer()

    @dp.callback_query(F.data.startswith("cat:"))
    async def open_category(c: CallbackQuery):
        category_id = int(c.data.split(":")[1])
        products = db.get_products_by_category(category_id)
        if not products:
            await c.answer("No products in this category yet.", show_alert=True)
            return
        await c.message.edit_text("🛍️ <b>Products:</b>", reply_markup=kb.products_kb(products))
        await c.answer()

    @dp.callback_query(F.data.startswith("prod:"))
    async def open_product(c: CallbackQuery):
        product_id = int(c.data.split(":")[1])
        p = db.get_product(product_id)
        if not p:
            await c.answer("This product is not available.", show_alert=True)
            return
        await c.message.edit_text(product_text(p), reply_markup=kb.product_kb(product_id))
        await c.answer()

    # ---------- CART ----------
    @dp.callback_query(F.data == "cart")
    async def cart(c: CallbackQuery, state: FSMContext):
        await state.clear()
        items = db.get_cart(c.from_user.id)
        total = db.cart_total(c.from_user.id)
        await c.message.edit_text(cart_text(items, total), reply_markup=kb.cart_kb(has_items=bool(items)))
        await c.answer()

    @dp.callback_query(F.data.startswith("cart_add:"))
    async def cart_add(c: CallbackQuery):
        pid = int(c.data.split(":")[1])
        db.add_to_cart(c.from_user.id, pid, +1)
        await c.answer("Added to cart")

    @dp.callback_query(F.data.startswith("cart_sub:"))
    async def cart_sub(c: CallbackQuery):
        pid = int(c.data.split(":")[1])
        db.add_to_cart(c.from_user.id, pid, -1)
        await c.answer("Updated")

    @dp.callback_query(F.data == "cart_clear")
    async def cart_clear(c: CallbackQuery):
        db.clear_cart(c.from_user.id)
        items = db.get_cart(c.from_user.id)
        total = db.cart_total(c.from_user.id)
        await c.message.edit_text(cart_text(items, total), reply_markup=kb.cart_kb(has_items=bool(items)))
        await c.answer("Cart cleared")

    # ---------- CHECKOUT ----------
    @dp.callback_query(F.data == "checkout")
    async def checkout_start(c: CallbackQuery, state: FSMContext):
        items = db.get_cart(c.from_user.id)
        if not items:
            await c.answer("Your cart is empty.", show_alert=True)
            return
        await state.set_state(Checkout.name)
        await c.message.edit_text("Enter your name:", reply_markup=kb.cancel_kb())
        await c.answer()

    @dp.callback_query(F.data == "cancel")
    async def cancel(c: CallbackQuery, state: FSMContext):
        await state.clear()
        await c.message.edit_text(START_TEXT, reply_markup=kb.main_menu_kb())
        await c.answer("Cancelled")

    @dp.message(Checkout.name)
    async def checkout_name(m: Message, state: FSMContext):
        name = (m.text or "").strip()
        if len(name) < 2:
            await m.answer("Name is too short. Try again:")
            return
        await state.update_data(name=name)
        await state.set_state(Checkout.phone)
        await m.answer("Enter your phone number (e.g. +380XXXXXXXXX):", reply_markup=kb.cancel_kb())

    @dp.message(Checkout.phone)
    async def checkout_phone(m: Message, state: FSMContext):
        phone = (m.text or "").strip()
        if len(phone) < 8:
            await m.answer("Phone number looks invalid. Try again:")
            return

        await state.update_data(phone=phone)
        await state.set_state(Checkout.city)
        await m.answer("Enter your city:", reply_markup=kb.cancel_kb())

    @dp.message(Checkout.city)
    async def checkout_city(m: Message, state: FSMContext):
        city = (m.text or "").strip()
        if len(city) < 2:
            await m.answer("City is too short. Try again:")
            return

        await state.update_data(city=city)
        await state.set_state(Checkout.delivery_method)
        await m.answer("Choose delivery method:", reply_markup=kb.delivery_method_kb())

    @dp.callback_query(F.data.startswith("delivery:"))
    async def delivery_choose(c: CallbackQuery, state: FSMContext):
        method_code = c.data.split(":")[1]
        # Save machine-readable code
        await state.update_data(delivery_method=method_code)

        await state.set_state(Checkout.address)

        if method_code == "pickup":
            prompt = "Enter pickup location (e.g. 'Main store, 10:00-18:00'):"
        elif method_code == "courier":
            prompt = "Enter delivery address (street, house, apt):"
        else:  # np
            prompt = "Enter Nova Poshta details (city, branch/parcel locker number):"

        await c.message.edit_text(prompt, reply_markup=kb.cancel_kb())
        await c.answer()

    @dp.message(Checkout.address)
    async def checkout_address(m: Message, state: FSMContext):
        address = (m.text or "").strip()
        if len(address) < 3:
            await m.answer("Address/branch is too short. Try again:")
            return

        await state.update_data(address=address)
        await state.set_state(Checkout.comment)
        await m.answer("Add a comment for the order (or type '-' for none):", reply_markup=kb.cancel_kb())

    @dp.message(Checkout.comment)
    async def checkout_finish(m: Message, state: FSMContext):
        comment = (m.text or "").strip()
        user_id = m.from_user.id

        items = db.get_cart(user_id)
        if not items:
            await state.clear()
            await m.answer("Your cart is empty. Returning to menu.", reply_markup=kb.main_menu_kb())
            return

        total = db.cart_total(user_id)
        data = await state.get_data()

        # Ensure delivery fields exist
        required = ("name", "phone", "city", "delivery_method", "address")
        if not all(k in data for k in required):
            await state.clear()
            await m.answer("Checkout session expired. Please try again.", reply_markup=kb.main_menu_kb())
            return

        # Human label for delivery method
        method_map = {
            "np": "Nova Poshta",
            "courier": "Courier",
            "pickup": "Pickup",
        }
        delivery_label = method_map.get(
            data["delivery_method"], data["delivery_method"])

        await state.update_data(comment=comment, delivery_label=delivery_label)
        await state.set_state(Checkout.confirm)

        summary = order_summary_text(
            items=items,
            total=total,
            name=data["name"],
            phone=data["phone"],
            city=data["city"],
            delivery_method_label=delivery_label,
            address=data["address"],
            comment=comment,
        )
        await m.answer(summary, reply_markup=kb.confirm_order_kb())

    @dp.message(Checkout.comment)
    async def checkout_finish(m: Message, state: FSMContext):
        comment = (m.text or "").strip()
        user_id = m.from_user.id

        items = db.get_cart(user_id)
        if not items:
            await state.clear()
            await m.answer("Your cart is empty. Returning to menu.", reply_markup=kb.main_menu_kb())
            return

        total = db.cart_total(user_id)
        data = await state.get_data()

        await state.update_data(comment=comment)
        await state.set_state(Checkout.confirm)

        summary = order_summary_text(
            items=items,
            total=total,
            name=data["name"],
            phone=data["phone"],
            comment=comment,
        )
        await m.answer(summary, reply_markup=kb.confirm_order_kb())

    # ---------- CONFIRM / CANCEL ORDER ----------
    @dp.callback_query(F.data == "order_cancel")
    async def order_cancel(c: CallbackQuery, state: FSMContext):
        await state.clear()
        await c.message.edit_text(
            "Checkout cancelled. You can continue shopping.",
            reply_markup=kb.main_menu_kb()
        )
        await c.answer("Cancelled")

    @dp.callback_query(F.data == "order_confirm")
    async def order_confirm(c: CallbackQuery, state: FSMContext):
        user_id = c.from_user.id

        data = await state.get_data()
        if not all(k in data for k in ("name", "phone", "comment")):
            await state.clear()
            await c.message.edit_text("Session expired. Please try again.", reply_markup=kb.main_menu_kb())
            await c.answer("Expired", show_alert=True)
            return

        items = db.get_cart(user_id)
        if not items:
            await state.clear()
            await c.message.edit_text("Your cart is empty.", reply_markup=kb.main_menu_kb())
            await c.answer("Empty", show_alert=True)
            return

        total = db.cart_total(user_id)

        lines = [
            "🧾 <b>NEW ORDER</b>",
            f"Customer: {_safe_user_label(c.from_user)}",
            f"User ID: <code>{user_id}</code>",
            "",
            "<b>Items:</b>",
        ]

        for it in items:
            line_total = int(it["qty"]) * int(it["price_uah"])
            lines.append(f"• {it['name']} × {it['qty']} = {line_total} UAH")

        comment = data["comment"]
        delivery_label = data.get(
            "delivery_label", data.get("delivery_method", "—"))
        lines += [
            "",
            f"<b>Total:</b> {total} UAH",
            "",
            f"<b>Name:</b> {data['name']}",
            f"<b>Phone:</b> {data['phone']}",
            f"<b>City:</b> {data.get('city','—')}",
            f"<b>Delivery:</b> {delivery_label}",
            f"<b>Address/Branch:</b> {data.get('address','—')}",
            f"<b>Comment:</b> {comment if comment != '-' else '—'}",
        ]

        await c.bot.send_message(chat_id=cfg.admin_chat_id, text="\n".join(lines))

        db.clear_cart(user_id)
        await state.clear()

        await c.message.edit_text(
            "✅ Order confirmed! We will contact you shortly.",
            reply_markup=kb.main_menu_kb()
        )
        await c.answer("Confirmed")

    await dp.start_polling(bot)
