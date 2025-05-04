# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from static_analyzer import StaticRepoParser  # ваш класс из примера, сохранённый в static_parser.py
from fastapi.middleware.cors import CORSMiddleware
import uuid

app = FastAPI()

# Разрешаем запросы с любого фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # или укажите список ваших доменов
    allow_methods=["POST", "GET"],  
    allow_headers=["*"],
)

class RepoRequest(BaseModel):
    repo_url: HttpUrl

class C4Response(BaseModel):
    containers: list
    components: list
    relationships: list

@app.post("/api/diagram", response_model=C4Response)
async def generate_diagram(data: RepoRequest):
    """
    1) Клонируем репозиторий из data.repo_url
    2) Строим граф и конвертим его в формат C4
    3) Возвращаем JSON с ключами containers, components, relationships
    """
    # создаём уникальную папку для клона, чтобы не мешать параллельным запросам
    parser = StaticRepoParser(data.repo_url, clone_dir=f"/tmp/{uuid.uuid4()}")

    try:
        parser.clone_repo()
    except Exception as e:
        # если не удалось клонировать (неверный URL, нет доступа и т.п.)
        raise HTTPException(status_code=400, detail=f"Не удалось клонировать репозиторий: {e}")

    try:
        graph = parser.build_graph()
        c4 = parser.graph_to_c4(graph)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при разборе кода: {e}")
    finally:
        # важно всегда чистить
        parser.cleanup()

    return c4
