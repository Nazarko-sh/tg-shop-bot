import aiosqlite
from typing import Any, Dict, List, Optional, Tuple
from app.utils import now_iso


class Database:
    def __init__(self, path: str):
        self.path = path

    async def init(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA foreign_keys=ON;")
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    lang TEXT NOT NULL DEFAULT 'ua',
                    ui_message_id INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    price_cents INTEGER NOT NULL DEFAULT 0,
                    stock INTEGER NOT NULL DEFAULT 0,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    photo_file_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(category_id) REFERENCES categories(id)
                );

                CREATE TABLE IF NOT EXISTS cart_items (
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    qty INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY (user_id, product_id),
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'NEW',
                    payment_method TEXT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    city TEXT NOT NULL,
                    delivery_method TEXT NOT NULL,
                    address TEXT NOT NULL,
                    comment TEXT,
                    total_cents INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    price_cents INTEGER NOT NULL,
                    qty INTEGER NOT NULL,
                    line_total_cents INTEGER NOT NULL,
                    FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
                CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
                """
            )
            await db.commit()

            # seed demo data if empty
            cur = await db.execute("SELECT COUNT(*) FROM categories;")
            (cnt,) = await cur.fetchone()
            if cnt == 0:
                now = now_iso()
                await db.execute(
                    "INSERT INTO categories(name,is_active,created_at,updated_at) VALUES(?,?,?,?)",
                    ("Demo category", 1, now, now),
                )
                await db.commit()
                cur2 = await db.execute("SELECT id FROM categories LIMIT 1;")
                (cat_id,) = await cur2.fetchone()
                await db.execute(
                    """
                    INSERT INTO products(category_id,title,description,price_cents,stock,is_active,photo_file_id,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        cat_id,
                        "Demo product",
                        "A nice demo product for your portfolio.",
                        19900,
                        10,
                        1,
                        None,
                        now,
                        now,
                    ),
                )
                await db.commit()

    # -------- users --------
    async def ensure_user(self, user_id: int) -> None:
        now = now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA foreign_keys=ON;")
            await db.execute(
                """
                INSERT INTO users(user_id, lang, created_at, updated_at)
                VALUES(?, 'ua', ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET updated_at=excluded.updated_at
                """,
                (user_id, now, now),
            )
            await db.commit()

    async def get_user_lang(self, user_id: int) -> str:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            row = await cur.fetchone()
            return row[0] if row else "ua"

    async def set_user_lang(self, user_id: int, lang: str) -> None:
        lang = lang if lang in ("ua", "en") else "ua"
        now = now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "UPDATE users SET lang=?, updated_at=? WHERE user_id=?",
                (lang, now, user_id),
            )
            await db.commit()

    async def get_ui_message_id(self, user_id: int) -> Optional[int]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("SELECT ui_message_id FROM users WHERE user_id=?", (user_id,))
            row = await cur.fetchone()
            return row[0] if row and row[0] else None

    async def set_ui_message_id(self, user_id: int, message_id: Optional[int]) -> None:
        now = now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "UPDATE users SET ui_message_id=?, updated_at=? WHERE user_id=?",
                (message_id, now, user_id),
            )
            await db.commit()

    # -------- catalog --------
    async def list_categories(self, only_active: bool = True) -> List[Dict[str, Any]]:
        q = "SELECT id,name,is_active FROM categories"
        if only_active:
            q += " WHERE is_active=1"
        q += " ORDER BY id DESC"
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(q)
            rows = await cur.fetchall()
        return [{"id": r[0], "name": r[1], "is_active": int(r[2])} for r in rows]

    async def create_category(self, name: str) -> int:
        now = now_iso()
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "INSERT INTO categories(name,is_active,created_at,updated_at) VALUES(?,?,?,?)",
                (name, 1, now, now),
            )
            await db.commit()
            return cur.lastrowid

    async def rename_category(self, category_id: int, name: str) -> None:
        now = now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "UPDATE categories SET name=?, updated_at=? WHERE id=?",
                (name, now, category_id),
            )
            await db.commit()

    async def set_category_active(self, category_id: int, active: bool) -> None:
        now = now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "UPDATE categories SET is_active=?, updated_at=? WHERE id=?",
                (1 if active else 0, now, category_id),
            )
            await db.commit()

    async def list_products(self, category_id: int, only_active: bool = True) -> List[Dict[str, Any]]:
        q = """
        SELECT id, title, description, price_cents, stock, is_active, photo_file_id
        FROM products WHERE category_id=?
        """
        params = [category_id]
        if only_active:
            q += " AND is_active=1"
        q += " ORDER BY id DESC"
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(q, params)
            rows = await cur.fetchall()
        return [
            {
                "id": r[0],
                "title": r[1],
                "description": r[2],
                "price_cents": int(r[3]),
                "stock": int(r[4]),
                "is_active": int(r[5]),
                "photo_file_id": r[6],
            }
            for r in rows
        ]

    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                """
                SELECT id, category_id, title, description, price_cents, stock, is_active, photo_file_id
                FROM products WHERE id=?
                """,
                (product_id,),
            )
            r = await cur.fetchone()
        if not r:
            return None
        return {
            "id": r[0],
            "category_id": r[1],
            "title": r[2],
            "description": r[3],
            "price_cents": int(r[4]),
            "stock": int(r[5]),
            "is_active": int(r[6]),
            "photo_file_id": r[7],
        }

    async def create_product(self, data: Dict[str, Any]) -> int:
        now = now_iso()
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                """
                INSERT INTO products(category_id,title,description,price_cents,stock,is_active,photo_file_id,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    data["category_id"],
                    data["title"],
                    data.get("description", ""),
                    data["price_cents"],
                    data["stock"],
                    1 if data.get("is_active", True) else 0,
                    data.get("photo_file_id"),
                    now,
                    now,
                ),
            )
            await db.commit()
            return cur.lastrowid

    async def update_product_fields(self, product_id: int, fields: Dict[str, Any]) -> None:
        if not fields:
            return
        now = now_iso()
        sets = []
        params = []
        for k, v in fields.items():
            sets.append(f"{k}=?")
            params.append(v)
        sets.append("updated_at=?")
        params.append(now)
        params.append(product_id)

        q = f"UPDATE products SET {', '.join(sets)} WHERE id=?"
        async with aiosqlite.connect(self.path) as db:
            await db.execute(q, params)
            await db.commit()

    # -------- cart --------
    async def get_cart(self, user_id: int) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                """
                SELECT ci.product_id, ci.qty, p.title, p.price_cents, p.stock, p.is_active
                FROM cart_items ci
                JOIN products p ON p.id = ci.product_id
                WHERE ci.user_id=?
                ORDER BY ci.product_id DESC
                """,
                (user_id,),
            )
            rows = await cur.fetchall()
        out = []
        for r in rows:
            out.append(
                {
                    "product_id": int(r[0]),
                    "qty": int(r[1]),
                    "title": r[2],
                    "price_cents": int(r[3]),
                    "stock": int(r[4]),
                    "is_active": int(r[5]),
                }
            )
        return out

    async def cart_set_qty(self, user_id: int, product_id: int, qty: int) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA foreign_keys=ON;")
            if qty <= 0:
                await db.execute(
                    "DELETE FROM cart_items WHERE user_id=? AND product_id=?",
                    (user_id, product_id),
                )
            else:
                await db.execute(
                    """
                    INSERT INTO cart_items(user_id, product_id, qty)
                    VALUES(?,?,?)
                    ON CONFLICT(user_id, product_id) DO UPDATE SET qty=excluded.qty
                    """,
                    (user_id, product_id, qty),
                )
            await db.commit()

    async def cart_clear(self, user_id: int) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM cart_items WHERE user_id=?", (user_id,))
            await db.commit()

    async def cart_get_qty(self, user_id: int, product_id: int) -> int:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT qty FROM cart_items WHERE user_id=? AND product_id=?",
                (user_id, product_id),
            )
            row = await cur.fetchone()
            return int(row[0]) if row else 0

    # -------- orders --------
    async def create_order_from_cart(
        self,
        user_id: int,
        name: str,
        phone: str,
        city: str,
        delivery_method: str,
        address: str,
        comment: Optional[str],
    ) -> Tuple[int, int]:
        """
        Transaction:
          - read cart
          - validate stock
          - insert order
          - insert order_items
          - decrement stock
          - clear cart
        Returns: (order_id, total_cents)
        """
        now = now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA foreign_keys=ON;")
            await db.execute("BEGIN;")

            cur = await db.execute(
                """
                SELECT ci.product_id, ci.qty, p.title, p.price_cents, p.stock, p.is_active
                FROM cart_items ci
                JOIN products p ON p.id = ci.product_id
                WHERE ci.user_id=?
                """,
                (user_id,),
            )
            cart = await cur.fetchall()
            if not cart:
                await db.execute("ROLLBACK;")
                raise ValueError("CART_EMPTY")

            # validate stock & active
            for (pid, qty, _title, _price, stock, is_active) in cart:
                if int(is_active) != 1:
                    await db.execute("ROLLBACK;")
                    raise ValueError("PRODUCT_INACTIVE")
                if int(qty) > int(stock):
                    await db.execute("ROLLBACK;")
                    raise ValueError("STOCK_NOT_ENOUGH")

            # create order
            cur2 = await db.execute(
                """
                INSERT INTO orders(user_id,status,payment_method,name,phone,city,delivery_method,address,comment,total_cents,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (user_id, "NEW", None, name, phone, city, delivery_method, address, comment, 0, now, now),
            )
            order_id = cur2.lastrowid

            total = 0
            for (pid, qty, title, price_cents, stock, _is_active) in cart:
                qty = int(qty)
                price = int(price_cents)
                line = qty * price
                total += line
                await db.execute(
                    """
                    INSERT INTO order_items(order_id,product_id,title,price_cents,qty,line_total_cents)
                    VALUES(?,?,?,?,?,?)
                    """,
                    (order_id, int(pid), str(title), price, qty, line),
                )
                # decrement stock
                await db.execute(
                    "UPDATE products SET stock = stock - ?, updated_at=? WHERE id=?",
                    (qty, now, int(pid)),
                )

            await db.execute(
                "UPDATE orders SET total_cents=?, updated_at=? WHERE id=?",
                (total, now, order_id),
            )
            await db.execute("DELETE FROM cart_items WHERE user_id=?", (user_id,))
            await db.commit()
            return int(order_id), int(total)

    async def list_user_orders(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                """
                SELECT id, status, payment_method, total_cents, created_at
                FROM orders
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            )
            rows = await cur.fetchall()
        return [
            {"id": int(r[0]), "status": r[1], "payment_method": r[2], "total_cents": int(r[3]), "created_at": r[4]}
            for r in rows
        ]

    async def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                """
                SELECT id,user_id,status,payment_method,name,phone,city,delivery_method,address,comment,total_cents,created_at,updated_at
                FROM orders WHERE id=?
                """,
                (order_id,),
            )
            r = await cur.fetchone()
        if not r:
            return None
        return {
            "id": int(r[0]),
            "user_id": int(r[1]),
            "status": r[2],
            "payment_method": r[3],
            "name": r[4],
            "phone": r[5],
            "city": r[6],
            "delivery_method": r[7],
            "address": r[8],
            "comment": r[9],
            "total_cents": int(r[10]),
            "created_at": r[11],
            "updated_at": r[12],
        }

    async def get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                """
                SELECT title, price_cents, qty, line_total_cents
                FROM order_items
                WHERE order_id=?
                ORDER BY id ASC
                """,
                (order_id,),
            )
            rows = await cur.fetchall()
        return [{"title": r[0], "price_cents": int(r[1]), "qty": int(r[2]), "line_total_cents": int(r[3])} for r in rows]

    async def set_order_payment_method(self, order_id: int, method: str) -> None:
        now = now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute("UPDATE orders SET payment_method=?, updated_at=? WHERE id=?", (method, now, order_id))
            await db.commit()

    async def admin_list_orders(self, limit: int = 20) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                """
                SELECT id,user_id,status,total_cents,created_at
                FROM orders
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = await cur.fetchall()
        return [{"id": int(r[0]), "user_id": int(r[1]), "status": r[2], "total_cents": int(r[3]), "created_at": r[4]} for r in rows]

    async def admin_set_order_status(self, order_id: int, status: str) -> None:
        now = now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute("UPDATE orders SET status=?, updated_at=? WHERE id=?", (status, now, order_id))
            await db.commit()

    async def admin_stats(self) -> Dict[str, int]:
        async with aiosqlite.connect(self.path) as db:
            cur1 = await db.execute("SELECT COUNT(*) FROM orders;")
            (cnt,) = await cur1.fetchone()
            cur2 = await db.execute("SELECT COALESCE(SUM(total_cents),0) FROM orders WHERE status IN ('NEW','PAID','IN_DELIVERY','DONE');")
            (rev,) = await cur2.fetchone()
        return {"orders_count": int(cnt), "revenue_cents": int(rev)}
