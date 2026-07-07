# backend/app/models.py
# Pydantic-схемы для запросов/ответов FastAPI

from typing import Optional
from pydantic import BaseModel


class Product(BaseModel):
    id: Optional[int] = None
    name: str            # название
    description: str = ""  # описание
    sku: str = ""         # артикул
    price: float = 0.0    # цена
    category: str = ""    # категория


class ProductScored(Product):
    score: float


class UploadResponse(BaseModel):
    status: str
    inserted: int


class SearchRequest(BaseModel):
    query: str


class SearchSources(BaseModel):
    bm25: list[ProductScored]
    vector: list[ProductScored]


class SearchResponse(BaseModel):
    answer: str
    sources: SearchSources
