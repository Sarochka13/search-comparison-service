# backend/app/search/semantic.py
# BM25-поиск. По заданию — через rank_bm25 с предварительным кэшированием
# (проще для демо, чем городить tsvector/pg_trgm в Postgres).

import re
import time
import logging

from rank_bm25 import BM25Okapi

from app.database.postgres import get_all_products

logger = logging.getLogger("search.bm25")

_bm25: BM25Okapi | None = None
_products_cache: list[dict] = []


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def build_index():
    """Пересобрать BM25-индекс из Postgres. Вызывается при старте
    и после каждой загрузки нового Excel-файла."""
    global _bm25, _products_cache
    _products_cache = get_all_products()
    corpus = [_tokenize(f"{p['name']} {p['description']}") for p in _products_cache]
    _bm25 = BM25Okapi(corpus) if corpus else None


def search_bm25(query: str, top_k: int = 3) -> list[dict]:
    if _bm25 is None or not _products_cache:
        return []

    t0 = time.time()
    scores = _bm25.get_scores(_tokenize(query))
    ranked = sorted(zip(_products_cache, scores), key=lambda x: x[1], reverse=True)[:top_k]
    logger.info("BM25 search took %.4fs", time.time() - t0)

    return [{**p, "score": float(s)} for p, s in ranked]
