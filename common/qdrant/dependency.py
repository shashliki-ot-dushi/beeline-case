from .base import get_qdrant_connection


def get_qdrant():
    yield get_qdrant_connection()