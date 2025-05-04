import os

from qdrant_client import QdrantClient


QDRANT_URL = os.getenv('QDRANT_URL')


client = QdrantClient(QDRANT_URL)


def get_qdrant_connection():
    return client