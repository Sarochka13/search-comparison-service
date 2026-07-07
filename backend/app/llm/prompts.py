# backend/app/llm/prompts.py
# Шаблоны промптов для LLM


def build_answer_prompt(query: str, bm25_results: list[dict], vector_results: list[dict]) -> str:
    """Собирает контекст из результатов обоих методов поиска (с дедупом по id)
    и просит LLM ответить пользователю только на основе найденных товаров."""

    seen = {}
    for r in bm25_results + vector_results:
        seen[r["id"]] = r

    lines = []
    for p in seen.values():
        lines.append(
            f"- {p['name']} (арт. {p.get('sku', '-')}, {p.get('price', '?')} руб., "
            f"категория: {p.get('category', '-')}): {p.get('description', '')}"
        )
    context = "\n".join(lines) if lines else "(товары не найдены)"

    return f"""Ты — консультант интернет-магазина. Отвечай на вопрос покупателя,
используя ТОЛЬКО товары из списка ниже. Если подходящего товара нет — так и скажи,
ничего не придумывай.

Товары:
{context}

Вопрос покупателя: {query}

Ответ (кратко, по-русски):"""
