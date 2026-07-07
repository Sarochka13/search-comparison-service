# backend/app/search/hybrid.py
# Запускает оба метода поиска, логирует время каждого (для сравнения
# производительности), собирает контекст и просит LLM сформулировать ответ.
#
# ВАЖНО: по ТЗ sources должен содержать TOP-3 от КАЖДОГО метода отдельно
# (для наглядности сравнения) — поэтому здесь нет слияния/переранжирования
# результатов в один список, только объединение контекста для LLM-промпта.

import time
import logging

from app.search.semantic import search_bm25
from app.search.vector import search_vector
from app.llm.ollama_client import generate_answer
from app.llm.prompts import build_answer_prompt

logger = logging.getLogger("search.hybrid")


def hybrid_search(query: str, top_k: int = 3) -> dict:
    t0 = time.time()

    bm25_results = search_bm25(query, top_k=top_k)
    vector_results = search_vector(query, top_k=top_k)

    prompt = build_answer_prompt(query, bm25_results, vector_results)
    answer = generate_answer(prompt)

    logger.info("Total hybrid_search took %.4fs", time.time() - t0)

    return {
        "answer": answer,
        "sources": {
            "bm25": bm25_results,
            "vector": vector_results,
        },
    }
