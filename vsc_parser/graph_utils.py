# graph_utils.py

import os, json
from neo4j import GraphDatabase
import networkx as nx
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    "bolt://84.54.56.225:7687",
    auth=("neo4j", "12345678")
)
# In-memory for deduplication
G = nx.MultiDiGraph()

def neo4j_query(query: str, **params):
    with driver.session() as s:
        s.run(query, **params)

def add_node(label: str, nid: str, **attrs):
    if G.has_node(nid):
        return
    G.add_node(nid)
    # simple CREATE — constraints on id must exist
    props = ", ".join(f"{k}: ${k}" for k in attrs)
    q = f"CREATE (n:{label} {{ id: $id{', ' + props if props else ''} }})"
    neo4j_query(q, id=nid, **attrs)

def add_edge(src: str, dst: str, rel: str):
    if G.has_edge(src, dst, key=rel):
        return
    G.add_edge(src, dst, key=rel)
    q = (
        "MATCH (a {id: $src}), (b {id: $dst}) "
        f"CREATE (a)-[:{rel}]->(b)"
    )
    neo4j_query(q, src=src, dst=dst)
