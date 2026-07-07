# backend/app/database/qdrant.py
# Подключение к Qdrant, создание коллекции, upsert и поиск

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.config import settings

_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
    return _client


def ensure_collection():
    """Создаёт коллекцию, если её ещё нет. Метрика — Cosine (стандартный выбор
    для текстовых эмбеддингов вроде nomic-embed-text)."""
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in existing:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=settings.embedding_dim, distance=Distance.COSINE),
        )


def upsert_products(products: list[dict], embeddings: list[list[float]]):
    client = get_client()
    points = [
        PointStruct(id=p["id"], vector=emb, payload=p)
        for p, emb in zip(products, embeddings)
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=points)


def search_vector(query_embedding: list[float], top_k: int = 3) -> list[dict]:
    client = get_client()
    hits = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_embedding,
        limit=top_k,
    ).points
    return [{**hit.payload, "score": hit.score} for hit in hits]
