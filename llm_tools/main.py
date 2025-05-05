import os
import traceback
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field, validator
from neo4j import GraphDatabase

# === Neo4j configuration ===
URI = os.getenv("NEO4J_URL")
USER, PASSWORD = os.getenv("NEO4J_AUTH").split("/")
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# === FastAPI app ===
app = FastAPI(title="Universal Neo4j Search API with Logs")

# === Request / Response models ===
class FilterItem(BaseModel):
    field: str = Field(..., description="Property name on the node")
    op: str = Field(..., description="Cypher operator, e.g., '=', '>', '<', 'CONTAINS'")
    value: Any = Field(..., description="Value to compare against")

    @validator('op')
    def validate_op(cls, v):
        allowed = {
            '=', '>', '<', '>=', '<=', '<>',
            'CONTAINS', 'STARTS WITH', 'ENDS WITH'
        }
        v_up = v.upper()
        if v_up not in allowed:
            raise ValueError(f"Unsupported operator: {v}")
        return v_up

class SearchRequest(BaseModel):
    label: Optional[str] = Field(None, description="Node label to match, e.g., 'Function'")
    filters: Optional[List[FilterItem]] = Field(None, description="List of filter conditions")
    connector: str = Field("AND", description="Logical connector between filters: AND or OR")
    limit: int = Field(25, gt=0, description="Maximum number of nodes to return")

    @validator('connector')
    def validate_connector(cls, v):
        v_up = v.upper()
        if v_up not in {"AND", "OR"}:
            raise ValueError("Connector must be 'AND' or 'OR'")
        return v_up

class NodeResult(BaseModel):
    labels: List[str]
    properties: Dict[str, Any]

class SearchResponse(BaseModel):
    nodes: List[NodeResult]
    logs: List[str]
    error: Optional[str] = None

class CypherRequest(BaseModel):
    query: str = Field(..., description="Any Cypher query, e.g. MATCH (n) RETURN n LIMIT 10")
    params: Optional[Dict[str, Any]] = Field(None, description="Map of parameters for the query")

class CypherResponse(BaseModel):
    records: List[Dict[str, Any]]
    logs: List[str]
    error: Optional[str] = None

# === /search endpoint ===
@app.post("/search", response_model=SearchResponse)
def search_endpoint(req: SearchRequest) -> SearchResponse:
    logs: List[str] = []
    logs.append("=== /search called ===")

    # Build label filter
    label_part = f":`{req.label}`" if req.label else ""
    logs.append(f"Label: {req.label or '<none>'}")

    # Build parameters
    params: Dict[str, Any] = {"limit": req.limit}
    logs.append(f"Limit: {req.limit}")

    # Build WHERE clause
    where_parts: List[str] = []
    if req.filters:
        for idx, f in enumerate(req.filters):
            pname = f"p{idx}"
            clause = f"n.`{f.field}` {f.op} ${pname}"
            where_parts.append(clause)
            params[pname] = f.value
            logs.append(f"Filter {idx}: {clause} (value={f.value})")

    where_clause = ""
    if where_parts:
        connector = f" {req.connector} "
        where_clause = " WHERE " + connector.join(where_parts)
        logs.append(f"WHERE clause: {where_clause}")

    # Final Cypher
    cypher = f"MATCH (n{label_part}){where_clause} RETURN n LIMIT $limit"
    logs.append(f"Cypher: {cypher}")
    logs.append(f"Params: {params}")

    # Execute
    try:
        with driver.session() as session:
            result = session.run(cypher, **params)
            nodes: List[NodeResult] = []
            for rec in result:
                node = rec["n"]
                nodes.append(NodeResult(
                    labels=list(node.labels),
                    properties=dict(node)
                ))
            logs.append(f"Returned {len(nodes)} nodes")
            return SearchResponse(nodes=nodes, logs=logs)
    except Exception as e:
        logs.append("!!! Error in /search:")
        logs.append(str(e))
        logs.append(traceback.format_exc())
        return SearchResponse(nodes=[], logs=logs, error=str(e))

# === /cypher endpoint ===
@app.post("/cypher", response_model=CypherResponse)
def cypher_endpoint(req: CypherRequest) -> CypherResponse:
    logs: List[str] = []
    logs.append("=== /cypher called ===")
    logs.append(f"Query: {req.query}")
    logs.append(f"Params: {req.params}")

    try:
        with driver.session() as session:
            result = session.run(req.query, **(req.params or {}))
            records: List[Dict[str, Any]] = []
            for rec in result:
                entry: Dict[str, Any] = {}
                for key in rec.keys():
                    val = rec[key]
                    if hasattr(val, "labels") and hasattr(val, "items"):
                        entry[key] = {
                            "labels": list(val.labels),
                            "properties": dict(val)
                        }
                    else:
                        entry[key] = val
                records.append(entry)
            logs.append(f"Returned {len(records)} records")
            return CypherResponse(records=records, logs=logs)
    except Exception as e:
        logs.append("!!! Error in /cypher:")
        logs.append(str(e))
        logs.append(traceback.format_exc())
        return CypherResponse(records=[], logs=logs, error=str(e))
