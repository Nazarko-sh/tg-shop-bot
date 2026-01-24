from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🗂️ Catalog", callback_data="catalog")
    b.button(text="🛒 Cart", callback_data="cart")
    b.adjust(2)
    return b.as_markup()

def categories_kb(categories) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for c in categories:
        b.button(text=c["name"], callback_data=f"cat:{c['id']}")
    b.button(text="🛒 Cart", callback_data="cart")
    b.button(text="⬅️ Menu", callback_data="menu")
    b.adjust(2)
    return b.as_markup()

def products_kb(products) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in products:
        b.button(text=f"{p['name']} — {p['price_uah']} UAH", callback_data=f"prod:{p['id']}")
    b.button(text="🛒 Cart", callback_data="cart")
    b.button(text="⬅️ Categories", callback_data="catalog")
    b.adjust(1)
    return b.as_markup()

def product_kb(product_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Add", callback_data=f"cart_add:{product_id}")
    b.button(text="➖ Remove", callback_data=f"cart_sub:{product_id}")
    b.button(text="🛒 Cart", callback_data="cart")
    b.button(text="⬅️ Back", callback_data="catalog")
    b.adjust(2)
    return b.as_markup()

def cart_kb(has_items: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if has_items:
        b.button(text="✅ Checkout", callback_data="checkout")
        b.button(text="🧹 Clear cart", callback_data="cart_clear")
    b.button(text="🗂️ Catalog", callback_data="catalog")
    b.button(text="⬅️ Menu", callback_data="menu")
    b.adjust(2)
    return b.as_markup()

def cancel_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="❌ Cancel", callback_data="cancel")
    return b.as_markup()

def confirm_order_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Confirm order", callback_data="order_confirm")
    b.button(text="❌ Cancel", callback_data="order_cancel")
    b.adjust(1)
    return b.as_markup()

def delivery_method_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="📦 Nova Poshta", callback_data="delivery:np")
    b.button(text="🚚 Courier", callback_data="delivery:courier")
    b.button(text="🏬 Pickup", callback_data="delivery:pickup")
    b.button(text="❌ Cancel", callback_data="cancel")
    b.adjust(1)
    return b.as_markup()
