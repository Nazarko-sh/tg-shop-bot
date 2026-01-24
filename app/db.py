import os
import sqlite3
from typing import List, Optional

class DB:
    def __init__(self, path: str):
        self.path = path
        self._ensure_dir()
        self._init()

    def _ensure_dir(self):
        folder = os.path.dirname(self.path)
        if folder:
            os.makedirs(folder, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self):
        with self._connect() as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS categories(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS products(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price_uah INTEGER NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(category_id) REFERENCES categories(id)
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS cart_items(
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                PRIMARY KEY(user_id, product_id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            );
            """)

            conn.commit()

        # Seed demo data only if empty
        if not self.get_categories():
            self.seed_demo()

    def seed_demo(self):
        categories = ["Coffee", "Chocolate", "Accessories"]
        with self._connect() as conn:
            cur = conn.cursor()
            for c in categories:
                cur.execute("INSERT OR IGNORE INTO categories(name) VALUES(?)", (c,))
            conn.commit()

        cat_map = {c["name"]: c["id"] for c in self.get_categories()}

        products = [
            (cat_map["Coffee"], "Ethiopia 250g", "Medium roast with berry notes.", 320),
            (cat_map["Coffee"], "Colombia 250g", "Nutty and caramel, well-balanced.", 300),
            (cat_map["Chocolate"], "Dark 70% 100g", "Cocoa-forward, low sugar.", 140),
            (cat_map["Accessories"], "V60 filters (100 pcs)", "Paper filters for V60 brewing.", 220),
        ]

        with self._connect() as conn:
            cur = conn.cursor()
            cur.executemany("""
                INSERT INTO products(category_id, name, description, price_uah, is_active)
                VALUES(?,?,?,?,1)
            """, products)
            conn.commit()

    # ---------- Catalog ----------
    def get_categories(self) -> List[sqlite3.Row]:
        with self._connect() as conn:
            return conn.execute("SELECT id, name FROM categories ORDER BY name").fetchall()

    def get_products_by_category(self, category_id: int) -> List[sqlite3.Row]:
        with self._connect() as conn:
            return conn.execute("""
                SELECT id, name, price_uah
                FROM products
                WHERE category_id=? AND is_active=1
                ORDER BY id DESC
            """, (category_id,)).fetchall()

    def get_product(self, product_id: int) -> Optional[sqlite3.Row]:
        with self._connect() as conn:
            return conn.execute("""
                SELECT p.id, p.name, p.description, p.price_uah, c.name AS category_name
                FROM products p
                JOIN categories c ON c.id=p.category_id
                WHERE p.id=? AND p.is_active=1
            """, (product_id,)).fetchone()

    # ---------- Cart ----------
    def add_to_cart(self, user_id: int, product_id: int, delta_qty: int):
        if delta_qty == 0:
            return

        with self._connect() as conn:
            cur = conn.cursor()
            row = cur.execute("""
                SELECT qty FROM cart_items WHERE user_id=? AND product_id=?
            """, (user_id, product_id)).fetchone()

            if row is None:
                if delta_qty > 0:
                    cur.execute("""
                        INSERT INTO cart_items(user_id, product_id, qty)
                        VALUES(?,?,?)
                    """, (user_id, product_id, delta_qty))
            else:
                new_qty = row["qty"] + delta_qty
                if new_qty <= 0:
                    cur.execute("""
                        DELETE FROM cart_items WHERE user_id=? AND product_id=?
                    """, (user_id, product_id))
                else:
                    cur.execute("""
                        UPDATE cart_items SET qty=? WHERE user_id=? AND product_id=?
                    """, (new_qty, user_id, product_id))

            conn.commit()

    def clear_cart(self, user_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM cart_items WHERE user_id=?", (user_id,))
            conn.commit()

    def get_cart(self, user_id: int) -> List[sqlite3.Row]:
        with self._connect() as conn:
            return conn.execute("""
                SELECT ci.product_id, ci.qty, p.name, p.price_uah
                FROM cart_items ci
                JOIN products p ON p.id=ci.product_id
                WHERE ci.user_id=?
                ORDER BY p.name
            """, (user_id,)).fetchall()

    def cart_total(self, user_id: int) -> int:
        items = self.get_cart(user_id)
        return sum(int(it["qty"]) * int(it["price_uah"]) for it in items)
