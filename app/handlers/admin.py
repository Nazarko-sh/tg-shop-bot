from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.db import Database
from app.config import Config
from app.i18n import t, ORDER_STATUSES
from app.keyboards import (
    kb_admin_panel,
    kb_admin_categories,
    kb_admin_category,
    kb_admin_products_root,
    kb_admin_products_list,
    kb_admin_product,
    kb_admin_orders,
    kb_admin_order,
)
from app.ui import send_or_edit, safe_delete_message
from app.states import AdminCategoryStates, AdminProductStates

router = Router()


def is_admin(cfg: Config, user_id: int) -> bool:
    return int(user_id) == int(cfg.admin_id)


async def show_admin_panel(bot, db: Database, cfg: Config, chat_id: int, user_id: int, lang: str):
    await send_or_edit(bot, db, chat_id, user_id, t(lang, "admin_panel"), kb_admin_panel(lang))


# ---------- PANEL ----------
@router.callback_query(F.data == "menu:admin")
async def cb_admin_from_menu(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)
    if not is_admin(cfg, callback.from_user.id):
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "admin_only"), None)
        return
    await show_admin_panel(callback.bot, db, cfg, callback.message.chat.id, callback.from_user.id, lang)


@router.callback_query(F.data == "admin:back")
async def cb_admin_back(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)
    await show_admin_panel(callback.bot, db, cfg, callback.message.chat.id, callback.from_user.id, lang)


# ---------- CATEGORIES ----------
@router.callback_query(F.data == "admin:cats")
async def cb_admin_cats(callback: CallbackQuery, db: Database, cfg: Config, state: FSMContext):
    await callback.answer()
    await state.clear()
    lang = await db.get_user_lang(callback.from_user.id)
    if not is_admin(cfg, callback.from_user.id):
        return
    cats = await db.list_categories(only_active=False)
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "🗂️ Categories:", kb_admin_categories(lang, cats))


@router.callback_query(F.data == "admin:cat:create")
async def cb_admin_cat_create(callback: CallbackQuery, db: Database, cfg: Config, state: FSMContext):
    await callback.answer()
    lang = await db.get_user_lang(callback.from_user.id)
    if not is_admin(cfg, callback.from_user.id):
        return
    await state.set_state(AdminCategoryStates.create_name)
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "Send category name:", None)


@router.message(AdminCategoryStates.create_name)
async def st_admin_cat_create(message: Message, db: Database, cfg: Config, state: FSMContext):
    await safe_delete_message(message)
    if not is_admin(cfg, message.from_user.id):
        return
    name = (message.text or "").strip()
    if len(name) < 2:
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Name too short. Send again:", None)
        return
    await db.create_category(name)
    await state.clear()
    lang = await db.get_user_lang(message.from_user.id)
    cats = await db.list_categories(only_active=False)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "done"), kb_admin_categories(lang, cats))


@router.callback_query(F.data.startswith("admin:cat:rename:"))
async def cb_admin_cat_rename(callback: CallbackQuery, db: Database, cfg: Config, state: FSMContext):
    await callback.answer()
    if not is_admin(cfg, callback.from_user.id):
        return
    cat_id = int(callback.data.split(":")[3])
    await state.update_data(cat_id=cat_id)
    await state.set_state(AdminCategoryStates.rename)
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, f"Send new name for category #{cat_id}:", None)


@router.message(AdminCategoryStates.rename)
async def st_admin_cat_rename(message: Message, db: Database, cfg: Config, state: FSMContext):
    await safe_delete_message(message)
    if not is_admin(cfg, message.from_user.id):
        return
    data = await state.get_data()
    cat_id = int(data["cat_id"])
    name = (message.text or "").strip()
    if len(name) < 2:
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Too short. Send again:", None)
        return
    await db.rename_category(cat_id, name)
    await state.clear()
    lang = await db.get_user_lang(message.from_user.id)
    cats = await db.list_categories(only_active=False)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "done"), kb_admin_categories(lang, cats))


@router.callback_query(F.data.startswith("admin:cat:archive:"))
async def cb_admin_cat_archive(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    if not is_admin(cfg, callback.from_user.id):
        return
    cat_id = int(callback.data.split(":")[3])
    await db.set_category_active(cat_id, False)
    lang = await db.get_user_lang(callback.from_user.id)
    cats = await db.list_categories(only_active=False)
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "done"), kb_admin_categories(lang, cats))


@router.callback_query(F.data.startswith("admin:cat:unarchive:"))
async def cb_admin_cat_unarchive(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    if not is_admin(cfg, callback.from_user.id):
        return
    cat_id = int(callback.data.split(":")[3])
    await db.set_category_active(cat_id, True)
    lang = await db.get_user_lang(callback.from_user.id)
    cats = await db.list_categories(only_active=False)
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "done"), kb_admin_categories(lang, cats))


@router.callback_query(F.data.startswith("admin:cat:") & ~F.data.startswith("admin:cat:rename:") & ~F.data.startswith("admin:cat:archive:") & ~F.data.startswith("admin:cat:unarchive:"))
async def cb_admin_cat_open(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    if not is_admin(cfg, callback.from_user.id):
        return
    cat_id = int(callback.data.split(":")[2])
    cats = await db.list_categories(only_active=False)
    cat = next((x for x in cats if x["id"] == cat_id), None)
    if not cat:
        return
    lang = await db.get_user_lang(callback.from_user.id)
    text = f"Category #{cat_id}\nName: {cat['name']}\nActive: {cat['is_active']}"
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, text, kb_admin_category(lang, cat_id, cat["is_active"]))


# ---------- PRODUCTS ----------
@router.callback_query(F.data == "admin:prods")
async def cb_admin_prods(callback: CallbackQuery, db: Database, cfg: Config, state: FSMContext):
    await callback.answer()
    await state.clear()
    if not is_admin(cfg, callback.from_user.id):
        return
    cats = await db.list_categories(only_active=False)
    lang = await db.get_user_lang(callback.from_user.id)
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "📦 Products: choose category", kb_admin_products_root(lang, cats))


@router.callback_query(F.data.startswith("admin:prods:cat:"))
async def cb_admin_prods_cat(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    if not is_admin(cfg, callback.from_user.id):
        return
    cat_id = int(callback.data.split(":")[3])
    products = await db.list_products(cat_id, only_active=False)
    lang = await db.get_user_lang(callback.from_user.id)
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, f"Products in category #{cat_id}:", kb_admin_products_list(lang, cat_id, products))


@router.callback_query(F.data == "admin:prod:create")
async def cb_admin_prod_create(callback: CallbackQuery, db: Database, cfg: Config, state: FSMContext):
    await callback.answer()
    if not is_admin(cfg, callback.from_user.id):
        return
    await state.clear()
    await state.set_state(AdminProductStates.create_title)
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "Send product title:", None)


@router.message(AdminProductStates.create_title)
async def st_prod_title(message: Message, db: Database, cfg: Config, state: FSMContext):
    await safe_delete_message(message)
    if not is_admin(cfg, message.from_user.id):
        return
    title = (message.text or "").strip()
    if len(title) < 2:
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Title too short. Send again:", None)
        return
    await state.update_data(title=title)
    await state.set_state(AdminProductStates.create_description)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Send description:", None)


@router.message(AdminProductStates.create_description)
async def st_prod_desc(message: Message, db: Database, cfg: Config, state: FSMContext):
    await safe_delete_message(message)
    if not is_admin(cfg, message.from_user.id):
        return
    await state.update_data(description=(message.text or "").strip())
    await state.set_state(AdminProductStates.create_price)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Send price (e.g. 199.99):", None)


@router.message(AdminProductStates.create_price)
async def st_prod_price(message: Message, db: Database, cfg: Config, state: FSMContext):
    await safe_delete_message(message)
    if not is_admin(cfg, message.from_user.id):
        return
    raw = (message.text or "").strip().replace(",", ".")
    try:
        val = float(raw)
        if val < 0:
            raise ValueError
        cents = int(round(val * 100))
    except Exception:
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Invalid price. Send again:", None)
        return
    await state.update_data(price_cents=cents)
    await state.set_state(AdminProductStates.create_category)

    cats = await db.list_categories(only_active=False)
    lines = ["Choose category by id:", ""]
    for c in cats:
        lines.append(f"{c['id']}: {c['name']} (active={c['is_active']})")
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "\n".join(lines), None)


@router.message(AdminProductStates.create_category)
async def st_prod_category(message: Message, db: Database, cfg: Config, state: FSMContext):
    await safe_delete_message(message)
    if not is_admin(cfg, message.from_user.id):
        return
    raw = (message.text or "").strip()
    if not raw.isdigit():
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Send numeric category id:", None)
        return
    cat_id = int(raw)
    cats = await db.list_categories(only_active=False)
    if not any(c["id"] == cat_id for c in cats):
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Category not found. Send again:", None)
        return

    await state.update_data(category_id=cat_id)
    await state.set_state(AdminProductStates.create_stock)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Send stock (integer):", None)


@router.message(AdminProductStates.create_stock)
async def st_prod_stock(message: Message, db: Database, cfg: Config, state: FSMContext):
    await safe_delete_message(message)
    if not is_admin(cfg, message.from_user.id):
        return
    raw = (message.text or "").strip()
    if not raw.isdigit():
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Send stock as integer:", None)
        return
    await state.update_data(stock=int(raw))
    await state.set_state(AdminProductStates.create_is_active)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Is active? Send 1 or 0:", None)


@router.message(AdminProductStates.create_is_active)
async def st_prod_active(message: Message, db: Database, cfg: Config, state: FSMContext):
    await safe_delete_message(message)
    if not is_admin(cfg, message.from_user.id):
        return
    raw = (message.text or "").strip()
    if raw not in ("0", "1"):
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Send 1 or 0:", None)
        return
    await state.update_data(is_active=(raw == "1"))
    await state.set_state(AdminProductStates.create_photo)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Optional: send photo or type SKIP", None)


@router.message(AdminProductStates.create_photo)
async def st_prod_photo(message: Message, db: Database, cfg: Config, state: FSMContext):
    await safe_delete_message(message)
    if not is_admin(cfg, message.from_user.id):
        return

    data = await state.get_data()
    photo_file_id = None

    if message.photo:
        photo_file_id = message.photo[-1].file_id
    else:
        if (message.text or "").strip().upper() != "SKIP":
            await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Send a photo or SKIP", None)
            return

    data["photo_file_id"] = photo_file_id
    prod_id = await db.create_product(data)
    await state.clear()

    lang = await db.get_user_lang(message.from_user.id)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, f"Created product #{prod_id}", kb_admin_product(lang, prod_id))


@router.callback_query(F.data.startswith("admin:prod:"))
async def cb_admin_prod(callback: CallbackQuery, db: Database, cfg: Config, state: FSMContext):
    await callback.answer()
    if not is_admin(cfg, callback.from_user.id):
        return

    parts = callback.data.split(":")
    lang = await db.get_user_lang(callback.from_user.id)

    # admin:prod:<id>
    if len(parts) == 3 and parts[2].isdigit():
        pid = int(parts[2])
        p = await db.get_product(pid)
        if not p:
            await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "Product not found.", None)
            return
        text = (
            f"Product #{pid}\n"
            f"Title: {p['title']}\n"
            f"Price: {p['price_cents']/100:.2f}\n"
            f"Stock: {p['stock']}\n"
            f"Active: {p['is_active']}\n"
            f"Category: {p['category_id']}\n"
            f"Has photo: {'yes' if p.get('photo_file_id') else 'no'}"
        )
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, text, kb_admin_product(lang, pid))
        return

    # admin:prod:delete:<id>
    if len(parts) == 4 and parts[2] == "delete":
        pid = int(parts[3])
        await db.update_product_fields(pid, {"is_active": 0})
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, t(lang, "done"), None)
        return

    # admin:prod:photo:<id>
    if len(parts) == 4 and parts[2] == "photo":
        pid = int(parts[3])
        await state.clear()
        await state.update_data(pid=pid)
        await state.set_state(AdminProductStates.wait_photo)
        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, f"Send new photo for product #{pid}:", None)
        return

    # admin:prod:edit:<id>:field
    if len(parts) == 5 and parts[2] == "edit":
        pid = int(parts[3])
        field = parts[4]
        await state.clear()
        await state.update_data(pid=pid, field=field)
        await state.set_state(AdminProductStates.edit_value)

        hint = {
            "title": "Send new title:",
            "description": "Send new description:",
            "price": "Send new price (e.g. 199.99):",
            "category": "Send new category id:",
            "stock": "Send new stock (int):",
            "is_active": "Send 1 or 0:",
        }.get(field, "Send new value:")

        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, hint, None)
        return


@router.message(AdminProductStates.wait_photo)
async def st_admin_photo(message: Message, db: Database, cfg: Config, state: FSMContext):
    await safe_delete_message(message)
    if not is_admin(cfg, message.from_user.id):
        return
    data = await state.get_data()
    pid = int(data.get("pid", 0))

    if not message.photo:
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Send photo please:", None)
        return

    file_id = message.photo[-1].file_id
    await db.update_product_fields(pid, {"photo_file_id": file_id})
    await state.clear()

    lang = await db.get_user_lang(message.from_user.id)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "done"), kb_admin_product(lang, pid))


@router.message(AdminProductStates.edit_value)
async def st_admin_edit_value(message: Message, db: Database, cfg: Config, state: FSMContext):
    await safe_delete_message(message)
    if not is_admin(cfg, message.from_user.id):
        return

    data = await state.get_data()
    pid = int(data.get("pid", 0))
    field = data.get("field", "")
    raw = (message.text or "").strip()

    fields = {}
    if field == "title":
        if len(raw) < 2:
            await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Too short, again:", None)
            return
        fields["title"] = raw

    elif field == "description":
        fields["description"] = raw

    elif field == "price":
        try:
            val = float(raw.replace(",", "."))
            if val < 0:
                raise ValueError
            fields["price_cents"] = int(round(val * 100))
        except Exception:
            await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Invalid price, again:", None)
            return

    elif field == "category":
        if not raw.isdigit():
            await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Send numeric category id:", None)
            return
        cat_id = int(raw)
        cats = await db.list_categories(only_active=False)
        if not any(c["id"] == cat_id for c in cats):
            await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Category not found, again:", None)
            return
        fields["category_id"] = cat_id

    elif field == "stock":
        if not raw.isdigit():
            await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Send stock integer:", None)
            return
        fields["stock"] = int(raw)

    elif field == "is_active":
        if raw not in ("0", "1"):
            await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Send 1 or 0:", None)
            return
        fields["is_active"] = int(raw)

    else:
        await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, "Unknown field.", None)
        return

    await db.update_product_fields(pid, fields)
    await state.clear()

    lang = await db.get_user_lang(message.from_user.id)
    await send_or_edit(message.bot, db, message.chat.id, message.from_user.id, t(lang, "done"), kb_admin_product(lang, pid))


# ---------- ADMIN ORDERS ----------
@router.callback_query(F.data == "admin:orders")
async def cb_admin_orders(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    if not is_admin(cfg, callback.from_user.id):
        return
    orders = await db.admin_list_orders(limit=20)
    lang = await db.get_user_lang(callback.from_user.id)
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "🧾 Last orders:", kb_admin_orders(lang, orders))


@router.callback_query(F.data.startswith("admin:order:"))
async def cb_admin_order_open(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    if not is_admin(cfg, callback.from_user.id):
        return

    parts = callback.data.split(":")
    lang = await db.get_user_lang(callback.from_user.id)

    # admin:order:status:<id>:<STATUS>
    if len(parts) == 5 and parts[2] == "status":
        order_id = int(parts[3])
        status = parts[4]
        if status not in ORDER_STATUSES:
            return

        await db.admin_set_order_status(order_id, status)
        order = await db.get_order(order_id)

        # notify user
        if order:
            try:
                await callback.bot.send_message(chat_id=order["user_id"], text=f"📦 Order #{order_id}\nStatus: {status}")
            except Exception:
                pass

        # refresh admin screen
        order = await db.get_order(order_id)

    # admin:order:<id>
    if len(parts) == 3 and parts[2].isdigit():
        order_id = int(parts[2])
        order = await db.get_order(order_id)
        if not order:
            await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "Order not found.", None)
            return

        items = await db.get_order_items(order_id)

        lines = [
            f"🧾 Order #{order_id}",
            "",
            f"User: {order['user_id']}",
            f"Status: {order['status']}",
            f"Total: {order['total_cents']/100:.2f}",
            f"Created: {order['created_at']}",
            "",
            f"Name: {order['name']}",
            f"Phone: {order['phone']}",
            f"City: {order['city']}",
            f"Delivery: {order['delivery_method']}",
            f"Address: {order['address']}",
            f"Comment: {order['comment'] or '-'}",
            "",
            "Items:",
        ]
        for it in items:
            lines.append(f"• {it['title']} — {it['qty']} × {it['price_cents']/100:.2f} = {it['line_total_cents']/100:.2f}")

        await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, "\n".join(lines), kb_admin_order(lang, order_id))


@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery, db: Database, cfg: Config):
    await callback.answer()
    if not is_admin(cfg, callback.from_user.id):
        return
    s = await db.admin_stats()
    lang = await db.get_user_lang(callback.from_user.id)
    text = f"📊 Stats\n\nOrders: {s['orders_count']}\nRevenue: {s['revenue_cents']/100:.2f}"
    await send_or_edit(callback.bot, db, callback.message.chat.id, callback.from_user.id, text, kb_admin_panel(lang))
