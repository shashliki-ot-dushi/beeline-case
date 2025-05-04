import logging

from qdrant_client.models import VectorParams, Distance

from .base import get_qdrant_connection


def ensure_collection_exists(collection_name: str):
    """Проверяем, существует ли коллекция, и baseсоздаем её, если не существует."""
    qdrant_client = get_qdrant_connection()
    try:
        collections = qdrant_client.get_collections()
        if collection_name not in collections:
            # Если коллекция не существует, создаем её
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
    except Exception as e:
        logging.error(f"Error checking or creating collection: {e}")