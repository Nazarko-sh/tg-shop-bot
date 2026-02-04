from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.i18n import t, ORDER_STATUSES, delivery_label


def kb_language() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Українська", callback_data="lang:ua")
    b.button(text="English", callback_data="lang:en")
    b.adjust(2)
    return b.as_markup()


def kb_menu(lang: str, is_admin: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "catalog"), callback_data="menu:catalog")
    b.button(text=t(lang, "cart"), callback_data="menu:cart")
    b.button(text=t(lang, "my_orders"), callback_data="menu:orders")
    b.button(text=t(lang, "support"), callback_data="menu:support")
    b.button(text=t(lang, "language"), callback_data="menu:language")
    if is_admin:
        b.button(text=t(lang, "admin"), callback_data="menu:admin")
    b.adjust(2, 2, 2)
    return b.as_markup()


def kb_back_menu(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "back"), callback_data="nav:back")
    b.button(text=t(lang, "menu"), callback_data="nav:menu")
    b.adjust(2)
    return b.as_markup()


def kb_catalog_categories(lang: str, categories) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for c in categories:
        b.button(text=f"📁 {c['name']}", callback_data=f"cat:{c['id']}")
    b.button(text=t(lang, "menu"), callback_data="nav:menu")
    b.adjust(1)
    return b.as_markup()


def kb_category_products(lang: str, category_id: int, products) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in products:
        stock = p["stock"]
        badge = "✅" if stock > 0 else "⛔"
        b.button(text=f"{badge} {p['title']}", callback_data=f"prod:{p['id']}")
    b.button(text=t(lang, "back"), callback_data=f"cat_back:{category_id}")
    b.button(text=t(lang, "menu"), callback_data="nav:menu")
    b.adjust(1)
    return b.as_markup()


def kb_product(lang: str, product_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "add"), callback_data=f"cart:add:{product_id}")
    b.button(text=t(lang, "remove"), callback_data=f"cart:rem:{product_id}")
    b.button(text=t(lang, "back"), callback_data="nav:catalog")
    b.button(text=t(lang, "cart"), callback_data="nav:cart")
    b.button(text=t(lang, "menu"), callback_data="nav:menu")
    b.adjust(2, 3)
    return b.as_markup()


def kb_cart(lang: str, cart_items) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    # per-item +/- row
    for it in cart_items:
        pid = it["product_id"]
        qty = it["qty"]
        b.row(
            InlineKeyboardButton(text=f"➖ {it['title']}", callback_data=f"cart:rem:{pid}"),
            InlineKeyboardButton(text=f"{qty} шт.", callback_data="noop"),
            InlineKeyboardButton(text=f"➕", callback_data=f"cart:add:{pid}"),
        )
    b.button(text=t(lang, "clear_cart"), callback_data="cart:clear")
    b.button(text=t(lang, "checkout"), callback_data="cart:checkout")
    b.button(text=t(lang, "menu"), callback_data="nav:menu")
    b.adjust(1, 1, 1)
    return b.as_markup()


def kb_checkout_delivery(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=f"📦 {delivery_label(lang,'NP')}", callback_data="del:NP")
    b.button(text=f"🚚 {delivery_label(lang,'COURIER')}", callback_data="del:COURIER")
    b.button(text=f"🏬 {delivery_label(lang,'PICKUP')}", callback_data="del:PICKUP")
    b.adjust(1)
    return b.as_markup()


def kb_confirm(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "edit_name"), callback_data="edit:name")
    b.button(text=t(lang, "edit_phone"), callback_data="edit:phone")
    b.button(text=t(lang, "edit_city"), callback_data="edit:city")
    b.button(text=t(lang, "edit_delivery"), callback_data="edit:delivery")
    b.button(text=t(lang, "edit_address"), callback_data="edit:address")
    b.button(text=t(lang, "edit_comment"), callback_data="edit:comment")
    b.adjust(2, 2, 2)

    b.button(text=t(lang, "confirm_order"), callback_data="order:confirm")
    b.button(text=t(lang, "back_to_cart"), callback_data="nav:cart")
    b.button(text=t(lang, "cancel"), callback_data="order:cancel")
    b.adjust(2, 1)
    return b.as_markup()


def kb_comment(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "skip"), callback_data="comment:skip")
    b.adjust(1)
    return b.as_markup()


def kb_payment(lang: str, order_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "pay_manual"), callback_data=f"pay:manual:{order_id}")
    b.button(text=t(lang, "pay_online"), callback_data=f"pay:online:{order_id}")
    b.button(text=t(lang, "my_orders"), callback_data="nav:orders")
    b.button(text=t(lang, "menu"), callback_data="nav:menu")
    b.adjust(2, 2)
    return b.as_markup()


def kb_order_details(lang: str, order_id: int, is_manual: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if is_manual:
        b.button(text=t(lang, "payment_details"), callback_data=f"paydetails:{order_id}")
    b.button(text=t(lang, "my_orders"), callback_data="nav:orders")
    b.button(text=t(lang, "menu"), callback_data="nav:menu")
    b.adjust(1, 2)
    return b.as_markup()


def kb_payment_details(lang: str, order_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "back"), callback_data=f"order:{order_id}")
    b.button(text=t(lang, "menu"), callback_data="nav:menu")
    b.adjust(2)
    return b.as_markup()


# ---------- admin ----------
def kb_admin_panel(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t(lang, "admin_categories"), callback_data="admin:cats")
    b.button(text=t(lang, "admin_products"), callback_data="admin:prods")
    b.button(text=t(lang, "admin_orders"), callback_data="admin:orders")
    b.button(text=t(lang, "admin_stats"), callback_data="admin:stats")
    b.button(text=t(lang, "menu"), callback_data="nav:menu")
    b.adjust(2, 2, 1)
    return b.as_markup()


def kb_admin_categories(lang: str, cats) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Create", callback_data="admin:cat:create")
    for c in cats:
        flag = "✅" if c["is_active"] else "🗄️"
        b.button(text=f"{flag} {c['name']}", callback_data=f"admin:cat:{c['id']}")
    b.button(text=t(lang, "admin_back"), callback_data="admin:back")
    b.adjust(1)
    return b.as_markup()


def kb_admin_category(lang: str, cat_id: int, is_active: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✏️ Rename", callback_data=f"admin:cat:rename:{cat_id}")
    if is_active:
        b.button(text="🗄️ Archive", callback_data=f"admin:cat:archive:{cat_id}")
    else:
        b.button(text="✅ Unarchive", callback_data=f"admin:cat:unarchive:{cat_id}")
    b.button(text=t(lang, "admin_back"), callback_data="admin:cats")
    b.adjust(1)
    return b.as_markup()


def kb_admin_products_root(lang: str, cats) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Create product", callback_data="admin:prod:create")
    for c in cats:
        b.button(text=f"📁 {c['name']}", callback_data=f"admin:prods:cat:{c['id']}")
    b.button(text=t(lang, "admin_back"), callback_data="admin:back")
    b.adjust(1)
    return b.as_markup()


def kb_admin_products_list(lang: str, cat_id: int, products) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in products:
        flag = "✅" if p["is_active"] else "🗑️"
        b.button(text=f"{flag} {p['title']}", callback_data=f"admin:prod:{p['id']}")
    b.button(text="➕ Create product", callback_data="admin:prod:create")
    b.button(text=t(lang, "admin_back"), callback_data="admin:prods")
    b.adjust(1)
    return b.as_markup()


def kb_admin_product(lang: str, product_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✏️ Title", callback_data=f"admin:prod:edit:{product_id}:title")
    b.button(text="✏️ Description", callback_data=f"admin:prod:edit:{product_id}:description")
    b.button(text="✏️ Price", callback_data=f"admin:prod:edit:{product_id}:price")
    b.button(text="✏️ Category", callback_data=f"admin:prod:edit:{product_id}:category")
    b.button(text="✏️ Stock", callback_data=f"admin:prod:edit:{product_id}:stock")
    b.button(text="✅/🗑️ Active", callback_data=f"admin:prod:edit:{product_id}:is_active")
    b.button(text="🖼️ Photo", callback_data=f"admin:prod:photo:{product_id}")
    b.button(text="🗑️ Soft delete", callback_data=f"admin:prod:delete:{product_id}")
    b.button(text=t(lang, "admin_back"), callback_data="admin:prods")
    b.adjust(2, 2, 2, 2, 1)
    return b.as_markup()


def kb_admin_orders(lang: str, orders) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for o in orders:
        b.button(text=f"#{o['id']} • {o['status']} • {o['total_cents']/100:.2f}", callback_data=f"admin:order:{o['id']}")
    b.button(text=t(lang, "admin_back"), callback_data="admin:back")
    b.adjust(1)
    return b.as_markup()


def kb_admin_order(lang: str, order_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for st in ORDER_STATUSES[1:]:  # skip NEW quick list? keep anyway
        b.button(text=st, callback_data=f"admin:order:status:{order_id}:{st}")
    b.button(text="REFRESH", callback_data=f"admin:order:{order_id}")
    b.button(text=t(lang, "admin_back"), callback_data="admin:orders")
    b.adjust(3, 2, 1)
    return b.as_markup()
