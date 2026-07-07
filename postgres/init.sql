-- Таблица товаров. Полнотекстовый поиск (BM25) реализован на стороне
-- Python (rank_bm25), поэтому tsvector/GIN-индекс тут не нужен.

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    sku TEXT DEFAULT '',
    price NUMERIC(12, 2) DEFAULT 0,
    category TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
