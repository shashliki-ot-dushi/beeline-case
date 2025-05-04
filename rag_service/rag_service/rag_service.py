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


def retrieve_similar_code(query: str, top_k: int = 5):
    """Поиск схожих фрагментов кода в Qdrant и извлечение связанных фрагментов"""
    
    # Генерация эмбеддинга для запроса
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Поиск по векторному индексу Qdrant
    results = qdrant_client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_embedding[0],
        limit=top_k
    )

    # Составляем список найденных фрагментов
    found_fragments = []
    for result in results:
        fragment_id = result.id
        score = result.score
        fragment_meta = result.payload
        
        # Проверка наличия поля 'path' в метаданных
        if 'path' not in fragment_meta:
            logging.warning(f"Поле 'path' отсутствует для фрагмента с ID {fragment_id}.")
            continue
        
        # Извлекаем код из Minio, используя метаданные (например, путь к файлу)
        file_path = fragment_meta['path']
        code = get_code_from_minio(file_path)
        
        found_fragments.append({
            "id": fragment_id,
            "score": score,
            "code": code,
            "name": fragment_meta['name'],
            "kind": fragment_meta['kind'],
            "path": fragment_meta['path'],
            "start_line": fragment_meta['start_line'],
            "end_line": fragment_meta['end_line'],
        })
    
    return found_fragments


def get_code_from_minio(file_path: str) -> str:
    """Получаем код из Minio по пути файла"""
    try:
        # Загружаем файл из Minio
        response = minio_client.get_object(MINIO_BUCKET, file_path)
        code = response.read().decode('utf-8')
        return code
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла из Minio: {e}")
        return ""


@app.post("/rag_query")
async def rag(query_request: QueryRequest):
    """API для поиска и генерации ответа с использованием RAG"""
    try:
        # Получаем похожие фрагменты кода из Qdrant и Minio
        similar_code = retrieve_similar_code(query_request.query)

        # Подготовка данных для генерации ответа LLM
        # Мы передаем код и метаданные найденных фрагментов в LLM для генерации ответа
        code_snippets = "\n".join([f"Code: {fragment['code']}" for fragment in similar_code])
        
        # Для этого примера просто возвращаем найденный код
        response = {
            "query": query_request.query,
            "found_code": similar_code,
            "llm_input": f"Query: {query_request.query}\n\n{code_snippets}\n\nPlease generate an answer based on the above code."
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))