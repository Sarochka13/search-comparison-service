# backend/app/database/postgres.py
# Подключение к Postgres, CRUD по товарам.
# Без пула соединений — коннект на операцию, для демо-сервиса этого достаточно.

import psycopg2
import psycopg2.extras

from app.config import settings


def get_conn():
    return psycopg2.connect(settings.postgres_dsn)


def init_db():
    """Создаёт таблицу products, если её ещё нет.

    Локально таблицу создавал postgres/init.sql через docker-entrypoint-initdb.d
    официального образа postgres — но на managed/облачном Postgres (например,
    приложение из каталога на Dockhost) этого механизма нет, поэтому дублируем
    создание таблицы прямо в коде при старте приложения."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            sku TEXT DEFAULT '',
            price NUMERIC(12, 2) DEFAULT 0,
            category TEXT DEFAULT ''
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
    conn.commit()
    cur.close()
    conn.close()


def insert_products(products: list[dict]) -> list[dict]:
    """Вставляет товары, возвращает их же, но уже с id из базы
    (id нужен дальше для upsert в Qdrant)."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    inserted = []
    for p in products:
        cur.execute(
            """
            INSERT INTO products (name, description, sku, price, category)
            VALUES (%(name)s, %(description)s, %(sku)s, %(price)s, %(category)s)
            RETURNING id, name, description, sku, price, category
            """,
            p,
        )
        inserted.append(dict(cur.fetchone()))

    conn.commit()
    cur.close()
    conn.close()
    return inserted


def get_all_products() -> list[dict]:
    """Все товары — используется для пересборки BM25-индекса в памяти."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, name, description, sku, price, category FROM products")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

