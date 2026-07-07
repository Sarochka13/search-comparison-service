# backend/app/llm/ollama_client.py
# Обёртка для локальной LLM (Ollama): эмбеддинги + генерация ответа.
#
# Используем /api/embed (актуальный эндпоинт, /api/embeddings официально
# считается устаревшим, хоть пока и работает).

import httpx

from app.config import settings

# nomic-embed-text рекомендует разные префиксы для запроса и для документа —
# это часть его инструкции по обучению, без префиксов качество поиска хуже
_QUERY_PREFIX = "search_query: "
_DOCUMENT_PREFIX = "search_document: "


def embed_text(text: str, is_query: bool = False) -> list[float]:
    prefix = _QUERY_PREFIX if is_query else _DOCUMENT_PREFIX
    resp = httpx.post(
        f"{settings.ollama_url}/api/embed",
        json={"model": settings.embedding_model, "input": prefix + text},
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


def generate_answer(prompt: str) -> str:
    resp = httpx.post(
        f"{settings.ollama_url}/api/generate",
        json={"model": settings.llm_model, "prompt": prompt, "stream": False},
        timeout=120.0,
    )
    resp.raise_for_status()
    return resp.json()["response"]
