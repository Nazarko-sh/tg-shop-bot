from typing import Dict

LANG_UA = "ua"
LANG_EN = "en"


TEXTS: Dict[str, Dict[str, str]] = {
    "choose_language": {
        "ua": "Привіт! Я магазин-бот 🛍️\nОберіть мову:",
        "en": "Hi! I’m a shop bot 🛍️\nChoose language:",
    },
    "language_set": {"ua": "Мову встановлено ✅", "en": "Language set ✅"},
    "menu_title": {
        "ua": "Головне меню 🏠",
        "en": "Main menu 🏠",
    },
    "catalog_title": {"ua": "Каталог 🗂️", "en": "Catalog 🗂️"},
    "cart_title": {"ua": "Кошик 🧺", "en": "Cart 🧺"},
    "orders_title": {"ua": "Мої замовлення 📦", "en": "My orders 📦"},
    "support_title": {"ua": "Підтримка 💬", "en": "Support 💬"},
    "back": {"ua": "⬅️ Назад", "en": "⬅️ Back"},
    "menu": {"ua": "🏠 Меню", "en": "🏠 Menu"},
    "catalog": {"ua": "🗂️ Каталог", "en": "🗂️ Catalog"},
    "cart": {"ua": "🧺 Кошик", "en": "🧺 Cart"},
    "my_orders": {"ua": "📦 Мої замовлення", "en": "📦 My orders"},
    "support": {"ua": "💬 Підтримка", "en": "💬 Support"},
    "language": {"ua": "🌐 Мова", "en": "🌐 Language"},
    "admin": {"ua": "🛠️ Адмін", "en": "🛠️ Admin"},
    "empty_catalog": {"ua": "Поки що немає активних категорій 🙂", "en": "No active categories yet 🙂"},
    "empty_products": {"ua": "У цій категорії поки немає товарів 🙂", "en": "No products in this category yet 🙂"},
    "product": {"ua": "Товар 🧾", "en": "Product 🧾"},
    "add": {"ua": "➕ Додати", "en": "➕ Add"},
    "remove": {"ua": "➖ Забрати", "en": "➖ Remove"},
    "clear_cart": {"ua": "🧹 Очистити кошик", "en": "🧹 Clear cart"},
    "checkout": {"ua": "✅ Оформити", "en": "✅ Checkout"},
    "cart_empty": {"ua": "Кошик порожній 🫥", "en": "Cart is empty 🫥"},
    "stock_not_enough": {"ua": "Немає стільки в наявності 😕", "en": "Not enough stock 😕"},
    "added_to_cart": {"ua": "Додано в кошик ✅", "en": "Added to cart ✅"},
    "removed_from_cart": {"ua": "Зменшено кількість ✅", "en": "Decreased ✅"},
    "checkout_intro": {"ua": "Оформлення замовлення ✍️", "en": "Checkout ✍️"},
    "ask_name": {"ua": "Введіть ім’я (мін. 2 символи):", "en": "Enter name (min 2 chars):"},
    "ask_phone": {"ua": "Введіть номер телефону (наприклад +380XXXXXXXXX):", "en": "Enter phone (e.g. +380XXXXXXXXX):"},
    "ask_city": {"ua": "Місто (мін. 2 символи):", "en": "City (min 2 chars):"},
    "ask_delivery": {"ua": "Оберіть спосіб доставки:", "en": "Choose delivery method:"},
    "ask_address": {"ua": "Адреса (мін. 5 символів):", "en": "Address (min 5 chars):"},
    "ask_comment": {"ua": "Коментар (необов’язково). Можна пропустити:", "en": "Comment (optional). You can skip:"},
    "skip": {"ua": "⏭️ Пропустити", "en": "⏭️ Skip"},
    "invalid_name": {"ua": "Ім’я закоротке. Спробуйте ще раз 🙏", "en": "Name is too short. Try again 🙏"},
    "invalid_phone": {"ua": "Некоректний номер. Спробуйте ще раз 🙏", "en": "Invalid phone. Try again 🙏"},
    "invalid_city": {"ua": "Місто закоротке. Спробуйте ще раз 🙏", "en": "City is too short. Try again 🙏"},
    "invalid_address": {"ua": "Адреса закоротка. Спробуйте ще раз 🙏", "en": "Address is too short. Try again 🙏"},
    "confirm_title": {"ua": "Підтвердження ✅", "en": "Confirm ✅"},
    "edit_name": {"ua": "✏️ Ім’я", "en": "✏️ Name"},
    "edit_phone": {"ua": "✏️ Телефон", "en": "✏️ Phone"},
    "edit_city": {"ua": "✏️ Місто", "en": "✏️ City"},
    "edit_delivery": {"ua": "✏️ Доставка", "en": "✏️ Delivery"},
    "edit_address": {"ua": "✏️ Адреса", "en": "✏️ Address"},
    "edit_comment": {"ua": "✏️ Коментар", "en": "✏️ Comment"},
    "confirm_order": {"ua": "✅ Підтвердити", "en": "✅ Confirm"},
    "back_to_cart": {"ua": "⬅️ До кошика", "en": "⬅️ To cart"},
    "cancel": {"ua": "❌ Скасувати", "en": "❌ Cancel"},
    "order_created": {"ua": "Замовлення створено 🎉", "en": "Order created 🎉"},
    "payment_title": {"ua": "Оплата 💳", "en": "Payment 💳"},
    "pay_manual": {"ua": "🏦 Ручна оплата", "en": "🏦 Manual"},
    "pay_online": {"ua": "💠 Online (demo)", "en": "💠 Online (demo)"},
    "coming_soon": {"ua": "Онлайн-оплата скоро буде доступна 😉 (демо)", "en": "Online payments coming soon 😉 (demo)"},
    "payment_details": {"ua": "🏦 Реквізити", "en": "🏦 Payment details"},
    "no_orders": {"ua": "У вас ще немає замовлень 🙂", "en": "You have no orders yet 🙂"},
    "order_status": {"ua": "Статус", "en": "Status"},
    "created_at": {"ua": "Створено", "en": "Created"},
    "admin_panel": {"ua": "Адмін-панель 🛠️", "en": "Admin panel 🛠️"},
    "admin_categories": {"ua": "🗂️ Категорії", "en": "🗂️ Categories"},
    "admin_products": {"ua": "📦 Товари", "en": "📦 Products"},
    "admin_orders": {"ua": "🧾 Замовлення", "en": "🧾 Orders"},
    "admin_stats": {"ua": "📊 Статистика", "en": "📊 Stats"},
    "admin_back": {"ua": "⬅️ Назад", "en": "⬅️ Back"},
    "admin_only": {"ua": "Ця дія тільки для адміністратора.", "en": "This action is admin-only."},
    "done": {"ua": "Готово ✅", "en": "Done ✅"},
    "status_updated": {"ua": "Статус оновлено ✅", "en": "Status updated ✅"},
}

DELIVERY_LABELS = {
    "NP": {"ua": "Нова Пошта", "en": "Nova Poshta"},
    "COURIER": {"ua": "Кур’єр", "en": "Courier"},
    "PICKUP": {"ua": "Самовивіз", "en": "Pickup"},
}

ORDER_STATUSES = ["NEW", "PAID", "IN_DELIVERY", "DONE", "CANCELED"]


def t(lang: str, key: str) -> str:
    lang = lang if lang in ("ua", "en") else "ua"
    return TEXTS.get(key, {}).get(lang) or TEXTS.get(key, {}).get("ua") or key


def delivery_label(lang: str, code: str) -> str:
    return DELIVERY_LABELS.get(code, {}).get(lang, code)
