# backend/app/main.py
# FastAPI приложение: сравнение BM25 и векторного поиска по товарам

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.models import SearchRequest, SearchResponse, UploadResponse
from app.utils.excel_parser import parse_excel
from app.database.postgres import insert_products, init_db
from app.database import qdrant as qdrant_db
from app.llm.ollama_client import embed_text
from app.search.semantic import build_index
from app.search.hybrid import hybrid_search

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # на старте: создаём таблицу (если её ещё нет), поднимаем коллекцию в Qdrant
    # и BM25-кэш из Postgres. Если базы ещё не готовы — не роняем приложение,
    # просто логируем: /upload_excel всё равно всё пересоздаст
    try:
        init_db()
        qdrant_db.ensure_collection()
        build_index()
    except Exception as e:
        logger.warning("Стартовая инициализация не удалась (ок, если БД ещё не готовы): %s", e)
    yield


app = FastAPI(title="RAG товары: BM25 vs Vector", lifespan=lifespan)


@app.post("/upload_excel", response_model=UploadResponse)
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Ожидается Excel-файл (.xlsx/.xls)")

    content = await file.read()
    products = parse_excel(content)
    if not products:
        raise HTTPException(400, "Не удалось найти товары в файле")

    inserted = insert_products(products)

    # эмбеддинги считаем по "название + описание" — этого обычно достаточно
    # для смыслового поиска по товару
    embeddings = [embed_text(f"{p['name']} {p['description']}") for p in inserted]

    qdrant_db.ensure_collection()
    qdrant_db.upsert_products(inserted, embeddings)

    build_index()  # обновляем BM25-кэш новыми товарами

    return UploadResponse(status="ok", inserted=len(inserted))


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(400, "Пустой запрос")
    result = hybrid_search(req.query)
    return SearchResponse(**result)


@app.get("/health")
def health():
    return {"status": "ok"}

