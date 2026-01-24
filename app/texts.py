START_TEXT = (
    "Welcome to the demo shop.\n\n"
    "Choose an option below:"
)

def product_text(p) -> str:
    return (
        f"🛍️ <b>{p['name']}</b>\n"
        f"Category: {p['category_name']}\n\n"
        f"{p['description']}\n\n"
        f"Price: <b>{p['price_uah']} UAH</b>"
    )

def cart_text(items, total: int) -> str:
    if not items:
        return "🛒 Your cart is empty."
    lines = ["🛒 <b>Your cart:</b>\n"]
    for it in items:
        line_total = int(it["qty"]) * int(it["price_uah"])
        lines.append(f"• {it['name']} × {it['qty']} = {line_total} UAH")
    lines.append(f"\n<b>Total: {total} UAH</b>")
    return "\n".join(lines)

def order_summary_text(
    items,
    total: int,
    name: str,
    phone: str,
    city: str,
    delivery_method_label: str,
    address: str,
    comment: str
) -> str:
    lines = ["🧾 <b>Order summary</b>", ""]
    for it in items:
        line_total = int(it["qty"]) * int(it["price_uah"])
        lines.append(f"• {it['name']} × {it['qty']} = {line_total} UAH")

    lines += [
        "",
        f"<b>Total:</b> {total} UAH",
        "",
        f"<b>Name:</b> {name}",
        f"<b>Phone:</b> {phone}",
        f"<b>City:</b> {city}",
        f"<b>Delivery:</b> {delivery_method_label}",
        f"<b>Address/Branch:</b> {address}",
        f"<b>Comment:</b> {comment if comment != '-' else '—'}",
        "",
        "Please confirm your order:",
    ]
    return "\n".join(lines)


