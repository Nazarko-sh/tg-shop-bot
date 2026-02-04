# Telegram Shop Bot 🛍️🤖  
**aiogram v3 • Python 3.11 • SQLite • UA/EN • One-message UI**

Portfolio-ready **Telegram Shop Bot** built with **Python 3.11** and **aiogram v3**.  
Clean **one-message UI**, multilingual interface (**UA/EN**), cart + checkout with validations, manual payments, order history, and an admin panel for real shop management.

✅ Stable callbacks (no infinite loading)  
✅ Safe UI formatting (`parse_mode=None`)  
✅ Minimal chat spam (most screens are edited)  

---

## ✨ Highlights
- 🌍 **UA / EN** — full bilingual experience
- 🧠 **One-message UI** — clean chat, no spam
- 🧺 **Cart + Checkout** — validations + confirm screen + edit fields
- 📦 **Stock control** — prevents overselling
- 🧾 **Orders history** — user + admin workflow
- 🛠️ **Admin panel** — categories/products/orders CRUD + stats

---

## 🧾 Features

### 👤 Customer side
- `/start` → choose **Українська / English**
- Main menu:
  - 📦 Catalog
  - 🧺 Cart
  - 🧾 My orders
  - 💬 Support
  - 🌍 Language
- Catalog:
  - categories (active only)
  - products (active only)
  - product screen: photo (if exists), description, price, stock
- Cart:
  - + / − quantity
  - clear cart
  - checkout
- Checkout (FSM):
  - name, phone, city
  - delivery method: NovaPoshta / Courier / Pickup
  - address + optional comment
  - validation + friendly retry messages
- Confirm screen (before creating order):
  - edit any field inline:
    - Edit name / phone / city / delivery / address / comment
  - Confirm / Back to cart / Cancel
- Payments:
  - Manual payment: details from `.env`
  - Online payment: demo placeholder
- My orders:
  - last 10 orders
  - order details: items, total, status, created date
  - payment details button (for manual payments)
- Support:
  - contact from `.env`

---

### 🛠️ Admin panel (ADMIN_ID only)
Access:
- `/admin`
- Menu → **Admin** (visible only for admin)

Admin tools:
- 🗂️ Categories CRUD
  - list
  - create
  - rename
  - archive / unarchive (`is_active`)
- 📦 Products CRUD
  - create product
  - edit fields: title / description / price / category / stock / is_active
  - soft delete (`is_active=0`)
  - upload/replace product photo:
    - admin sends photo → saved as `photo_file_id`
- 🧾 Orders management
  - list recent orders
  - open order details
  - change order status:
    - `PAID`
    - `IN_DELIVERY`
    - `DONE`
    - `CANCELED`
  - notify user when status changes
- 📊 Stats
  - orders count
  - total revenue

---

## 🧠 One-message UI (Clean Chat)
The bot uses a **single main UI message** for navigation:
- screens update via `editMessageText / editMessageMedia`
- user checkout inputs are deleted after processing
- reduces clutter and feels like a real application

---

## ⚙️ Tech Stack
- **Python 3.11**
- **aiogram 3.x**
- **SQLite** (`shop.db`) + `aiosqlite`
- `.env` config
- Logging (INFO/ERROR) + global error handler
- Callback stability:
  - `callback.answer()` is always called ✅

---

## 📁 Project Structure

