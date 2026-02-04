# Telegram Shop Bot (aiogram v3) — Portfolio Project 🛍️

A stable “one-message UI” Telegram shop bot:
- Python 3.11 + aiogram v3
- SQLite (`shop.db`) + `aiosqlite`
- UA/EN languages stored in DB
- Catalog (categories/products), stock control
- Cart (inline +/-), clear, checkout
- Checkout FSM with validations + Confirm screen with inline edit
- Orders history + order details + manual payment details
- Support from .env
- Admin panel: CRUD categories & products, product photo via file_id, order statuses + notify user, stats

## 1) Setup (Python 3.11)

### Create venv
```bash
python -m venv .venv
