import os

from neo4j import GraphDatabase


NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_AUTH = os.getenv("NEO4J_AUTH", "neo4j/123")


driver = GraphDatabase.driver(
    NEO4J_URL,
    auth=tuple(NEO4J_AUTH.split("/"))
)


def get_neo4j_connection():
    return driver.session()