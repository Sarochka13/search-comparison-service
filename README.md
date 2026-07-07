# RAG на товарах: BM25 vs Vector (Задача 1)

Микросервис для сравнения семантического (BM25) и векторного поиска по товарам,
с ответом от локальной LLM через Ollama.

## Запуск

```bash
docker compose up -d --build
```

Первый запуск: нужно скачать модели в контейнер ollama (делается один раз,
веса останутся в volume `ollama_data`):

```bash
docker exec -it rag_ollama ollama pull nomic-embed-text:v1.5
docker exec -it rag_ollama ollama pull llama3.2:3b
```

Если `llama3.2:3b` тормозит на вашей машине — замените `LLM_MODEL` в `.env`
на `phi3:mini` и сделайте `docker exec -it rag_ollama ollama pull phi3:mini`,
затем `docker compose restart backend`.

Проверить, что backend поднялся:

```bash
curl http://localhost:8000/health
```

## Загрузка товаров

```bash
python scripts/seed_data.py
```

или вручную:

```bash
curl -X POST http://localhost:8000/upload_excel -F "file=@ваш_файл.xlsx"
```

Ожидаемые колонки в Excel (регистр не важен): `название`, `описание`,
`артикул`, `цена`, `категория`.

## Поиск

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "нужен дешевый ноутбук для работы"}'
```

Ответ:

```json
{
  "answer": "...",
  "sources": {
    "bm25": [ {"id": 1, "name": "...", "score": 3.21, ...}, ... ],
    "vector": [ {"id": 3, "name": "...", "score": 0.87, ...}, ... ]
  }
}
```

`bm25` и `vector` — top-3 от каждого метода отдельно (не смешаны и не
переранжированы) — так и требовалось по заданию, для наглядного сравнения.
Время выполнения каждого метода пишется в логи backend (`docker compose logs -f backend`).

## Структура

Смотри `docker-compose.yml` и `backend/app/`. Основная логика:

- `search/semantic.py` — BM25 (`rank_bm25`), индекс в памяти, кэш из Postgres
- `search/vector.py` — эмбеддинг запроса через Ollama + поиск в Qdrant
- `search/hybrid.py` — вызывает оба метода, логирует тайминги, собирает контекст
  для LLM и просит её сформулировать ответ
- `llm/ollama_client.py` — обёртка над `/api/embed` и `/api/generate`

## Что не покрыто (нет в этом ТЗ)

В дереве проекта есть `categorization/`, `csv_parser.py`, `create_golden_standard.py` —
это, судя по всему, относится к отдельной задаче (категоризация банковских
транзакций), для которой пока нет условия. Не реализовывал, чтобы не гадать
на пустом месте.
