import os, io, ast, uuid, logging
from pathlib import Path

import numpy as np
from git import Repo

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from minio import Minio
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from sentence_transformers import SentenceTransformer

from common.schemas.user import User
from common.schemas.project import Project

from common.auth.dependency import get_current_user
from common.s3.dependency import get_s3
from common.database.dependency import get_db
from common.qdrant.dependency import get_qdrant
from common.qdrant.collections import ensure_collection_exists
from common.ast.pipeline import CacheManager, CodeParser, Indexer

# Инициализация приложения
app = FastAPI()

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

QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "documents")

# Подключение к Qdrant
qdrant_client = QdrantClient(os.getenv('QDRANT_URL'))

model = SentenceTransformer('all-MiniLM-L6-v2')  # Или другая модель по вашему выбору

# Создание бакета в Minio, если его нет
MINIO_BUCKET = os.getenv('AWS_S3_BUCKET')
if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)


@app.post("/ingest/{project_id}")
async def ingest_repository(
    project_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    minio_client: Minio = Depends(get_s3),
    qdrant_client: QdrantClient = Depends(get_qdrant)
):
    project = db.query(Project).filter(Project.id == str(project_id)).first()
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to ingest this project")

    try:
        repo_data = download_repository(project.name)
        ast_data, files_info = split_repository(repo_data)

        # ... загрузка метаданных и Qdrant как было ...

        # Сохраняем .py файлы, сохраняя папки внутри ключа
        for file_info in files_info:
            with open(file_info["file_path"], 'rb') as f:
                data = f.read()
            # ключ будет вида "repository_code/path/to/file.py"
            key = f"{project_id}/repository_code/{file_info['relative_path']}"
            minio_client.put_object(
                MINIO_BUCKET,
                key,
                io.BytesIO(data),
                len(data)
            )

        ensure_collection_exists(project_id)
        qdrant_client.upsert(
            collection_name=project_id,
            points=extract_vectors(ast_data)
        )

        return {"status": "success", "message": "Repository ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Вспомогательные функции

def download_repository(url: str) -> str:
    """Скачиваем репозиторий с использованием Git"""
    repo_dir = "/tmp/repository"
    if os.path.exists(repo_dir):
        os.system(f"rm -rf {repo_dir}")
    os.system(f"git clone {url} {repo_dir}")
    return repo_dir


def split_repository(repo_dir: str) -> dict:
    """Разбиение репозитория на AST и байткод"""
    ast_data = []
    files_info = []

    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                # относительный путь от корня репозитория, с Unix-разделителями
                rel_path = Path(file_path).relative_to(repo_dir).as_posix()

                fragments = extract_defs_from_file(file_path, repo_dir)
                ast_data.extend(fragments)

                files_info.append({
                    "file_path": file_path,
                    "relative_path": rel_path,
                })

    return ast_data, files_info

def extract_defs_from_file(file_path: str, repo_path: str) -> list:
    """Извлечение функций и классов из исходного файла Python"""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()  # Читаем весь исходный код

    tree = ast.parse(source)  # Парсим исходный код в AST
    fragments = []  # Список для хранения фрагментов

    for node in ast.walk(tree):
        # Ищем только функции и классы
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno
            end = getattr(node, 'end_lineno', node.lineno)
            
            # Извлекаем фрагмент исходного кода для функции или класса
            code_seg = ast.get_source_segment(source, node)
            
            if code_seg is None:
                logging.error(f"Не удалось извлечь исходный код для {node.name} в {file_path}")
                continue  # Если код не найден, пропускаем этот фрагмент

            # Получаем относительный путь к файлу в репозитории
            context = os.path.relpath(file_path, repo_path)
            kind = type(node).__name__  # Получаем тип узла (например, FunctionDef или ClassDef)
            
            # Добавляем фрагмент в список
            fragments.append({
                "name": node.name,
                "kind": kind,
                "path": context,
                "start_line": start,
                "end_line": end,
                "code": code_seg  # Добавляем сам код
            })

    return fragments

def parse_bytecode(bytecode, file_path: str) -> dict:
    """Парсинг байткода для извлечения инструкций"""
    bytecode_instructions = [f"Instruction {i}" for i in range(10)]  # Пример
    return {
        'kind': 'Bytecode',
        'path': file_path,
        'bytecode': "\n".join(bytecode_instructions),
        'start_line': 1
    }

def extract_vectors(ast_data: list) -> list:
    # Собираем фрагменты кода
    texts = [item['code'] for item in ast_data]
    
    # Получаем эмбеддинги для каждого фрагмента
    embeddings = embed_texts(texts)

    # Формируем точки для вставки в Qdrant
    points = []
    for idx, item in enumerate(ast_data):
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embeddings[idx].tolist(),
            payload={
                "path":       item["path"],
                "name":       item["name"],
                "kind":       item["kind"],
                "start_line": item["start_line"],
                "end_line":   item["end_line"],
            },
        ))
    return points

def embed_texts(texts, batch_size=50):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embs = model.encode(batch, convert_to_numpy=True)
        embeddings.append(embs)
    return np.vstack(embeddings).astype('float32')