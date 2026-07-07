# backend/app/search/vector.py
# Векторный поиск: эмбеддинг запроса через Ollama + поиск в Qdrant

import time
import logging

from app.llm.ollama_client import embed_text
from app.database.qdrant import search_vector as qdrant_search

logger = logging.getLogger("search.vector")


def search_vector(query: str, top_k: int = 3) -> list[dict]:
    t0 = time.time()
    embedding = embed_text(query, is_query=True)
    results = qdrant_search(embedding, top_k=top_k)
    logger.info("Vector search took %.4fs", time.time() - t0)
    return results
