from .base import get_neo4j_connetion


def get_neo4j():
    yield get_neo4j_connection()