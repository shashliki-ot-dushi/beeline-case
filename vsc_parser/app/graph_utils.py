import re

from common.neo4j.base import get_neo4j_connection


session = get_neo4j_connection()


def neo4j_query(query: str, **params):
    session.run(query, **params)


def add_node(G, label: str, nid: str, project_uuid: str, **attrs):
    if G.has_node(nid):
        return
    G.add_node(nid)

    context_label = escape_label(f"Context_{project_uuid}")
    all_labels = f"{label}:{context_label}"
    props = ", ".join(f"{k}: ${k}" for k in attrs)
    q = f"CREATE (n:{all_labels} {{ id: $id{', ' + props if props else ''} }})"
    neo4j_query(q, id=nid, **attrs)


def add_edge(G, src: str, dst: str, rel: str, project_uuid: str):
    if G.has_edge(src, dst, key=rel):
        return
    G.add_edge(src, dst, key=rel)

    context_label = escape_label(f"Context_{project_uuid}")
    q = (
        f"MATCH (a:{context_label} {{id: $src}}), "
        f"(b:{context_label} {{id: $dst}}) "
        f"CREATE (a)-[:{rel}]->(b)"
    )
    neo4j_query(q, src=src, dst=dst)


def escape_label(label: str) -> str:
    # Replace all non-alphanumeric characters with underscores
    return re.sub(r'\W', '_', label)
