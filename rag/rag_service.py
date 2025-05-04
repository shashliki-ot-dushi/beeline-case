import os, logging, uuid
from typing import List, Dict

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Session

from sentence_transformers import SentenceTransformer

from common.auth.dependency import get_current_user
from common.schemas.user import User
from common.schemas.project import Project
from common.s3.base import get_s3_connection, MINIO_URL
from common.s3.download import get_file
from common.database.dependency import get_db
from common.qdrant.base import get_qdrant_connection

app = FastAPI()

# Инициализация модели для эмбеддингов
model = SentenceTransformer('all-MiniLM-L6-v2')

# Подключение к Minio
logging.basicConfig(level=logging.DEBUG)
logging.debug(f"Connecting to Minio at {MINIO_URL}")

minio_client = get_s3_connection()
qdrant_client = get_qdrant_connection()

# Константы для хранения в Minio и Qdrant
MINIO_BUCKET = os.getenv('AWS_S3_BUCKET')
QDRANT_COLLECTION = 'documents'


class QueryRequest(BaseModel):
    query: str  # Запрос для поиска схожих фрагментов кода


def retrieve_similar_code(project: str, query: str, top_k: int = 5) -> List[Dict]:
    # Генерируем эмбеддинг
    query_emb = model.encode([query], convert_to_numpy=True)[0]

    # Ищем в Qdrant с payload
    results = qdrant_client.search(
        collection_name=project,
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

        full_code = get_file("repository_code", meta["path"])
        lines = full_code.splitlines()
        start, end = meta["start_line"], meta["end_line"]
        snippet = "\n".join(lines[start-1:end])

        structures.append({
            "name": meta["name"],
            "type": meta["kind"],
            "code": snippet
        })

    return structures


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


@app.post("/rag-query/{project_id}")
async def rag_query(
    project_id: uuid.UUID,
    req: QueryRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == str(project_id)).first()
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to ingest this project")

    try:
        structures = retrieve_similar_code(project_id, req.query)
        llm_input = build_llm_input(req.query, structures)
        return {
            "query": req.query,
            "structures": structures,
            "llm_input": llm_input
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))