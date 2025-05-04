from typing import List, Dict
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tempfile
import random
import shutil
from git import Repo
from pathlib import Path
import networkx as nx
import dis
import re
import numpy as np
import boto3
import os
from minio import Minio
import logging
import json
from qdrant_client import QdrantClient
import io
from qdrant_client.models import PointStruct, VectorParams, Distance
# Импортируем ваши классы из прототипа
from common.ast_pipeline import CacheManager, CodeParser, Indexer
import ast  # Добавили импорт ast
from sentence_transformers import SentenceTransformer


app = FastAPI()

# Инициализация модели для эмбеддингов
model = SentenceTransformer('all-MiniLM-L6-v2')

# Подключение к Minio
logging.basicConfig(level=logging.DEBUG)

minio_url = os.getenv('AWS_ENDPOINT_URL', 'minio:9000').strip('/')
logging.debug(f"Connecting to Minio at {minio_url}")

minio_client = Minio(
    minio_url,
    access_key=os.getenv('AWS_ACCESS_KEY_ID'),
    secret_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    secure=False
)

# Подключение к Qdrant
qdrant_client = QdrantClient(os.getenv('QDRANT_URL'))

# Константы для хранения в Minio и Qdrant
MINIO_BUCKET = os.getenv('AWS_S3_BUCKET')
QDRANT_COLLECTION = 'documents'


class QueryRequest(BaseModel):
    query: str  # Запрос для поиска схожих фрагментов кода


def retrieve_similar_code(query: str, top_k: int = 5) -> List[Dict]:
    # Генерируем эмбеддинг
    query_emb = model.encode([query], convert_to_numpy=True)[0]

    # Ищем в Qdrant с payload
    results = qdrant_client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_emb,
        limit=top_k,
        with_payload=["path", "name", "kind", "start_line", "end_line"]
    )

    structures: List[Dict] = []
    for pt in results:
        meta = pt.payload or {}
        if not all(k in meta for k in ("path", "name", "kind", "start_line", "end_line")):
            logging.warning(f"Неполные метаданные у точки {pt.id}")
            continue

        full_code = get_code_from_minio(meta["path"])
        lines = full_code.splitlines()
        start, end = meta["start_line"], meta["end_line"]
        snippet = "\n".join(lines[start-1:end])

        structures.append({
            "name": meta["name"],
            "type": meta["kind"],
            "code": snippet
        })

    return structures


def get_code_from_minio(file_path: str) -> str:
    """Получаем код из Minio по пути файла"""
    try:
        key = f"repository_code/{file_path}"
        response = minio_client.get_object(MINIO_BUCKET, key)
        code = response.read().decode('utf-8')
        return code
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла из Minio: {e}")
        return ""


def build_llm_input(query: str, structures: List[Dict]) -> str:
    prompt = [f"Запрос: {query}", "Используя следующие фрагменты кода, ответьте на запрос:\n"]
    for idx, s in enumerate(structures, 1):
        prompt.append(f"Фрагмент {idx}:")
        prompt.append(f"  Name: {s['name']}")
        prompt.append(f"  Type: {s['type']}")
        prompt.append("  Code:")
        prompt.append(f"```\n{s['code']}\n```")
    prompt.append("\nПожалуйста, сформируйте развёрнутый ответ, ссылаясь на эти фрагменты.")
    return "\n".join(prompt)


@app.post("/rag-query")
async def rag_query(req: QueryRequest):
    try:
        structures = retrieve_similar_code(req.query)
        llm_input = build_llm_input(req.query, structures)
        return {
            "query": req.query,
            "structures": structures,
            "llm_input": llm_input
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))