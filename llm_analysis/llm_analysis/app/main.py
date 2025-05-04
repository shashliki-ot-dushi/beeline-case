import os
import shutil
import tempfile
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from sqlalchemy.exc import SQLAlchemyError
import time
from sqlmodel import Session
from datetime import datetime
from app.models import RepoRequest, DiagramResponse
from app.db import init_db, get_session, Job, DiagramElement
from app.parser import RepoParser
from app.static_analyzer import StaticRepoParser
from app.diagram import DiagramBuilder
init_db()
app = FastAPI(title="C4 Generator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Хранилище состояния задач: job_id -> {status, progress, diagram?, error?}
tasks: Dict[str, Dict[str, Any]] = {}

@app.post("/generate-diagram")
async def start_generation(req: RepoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    tasks[job_id] = {"status": "pending", "progress": 0.0}
    # создаём запись Job в БД
    with next(get_session()) as session:
        session.add(Job(
            job_id=job_id,
            repo_url=req.repo_url,
            use_gpt=req.use_gpt,
            status="pending",
            progress=0.0
        ))
        session.commit()
    background_tasks.add_task(run_generation, job_id, req.repo_url, req.use_gpt)
    return {"job_id": job_id, "status": "pending", "progress": 0.0}

@app.get("/generate-diagram/{job_id}", summary="Получить прогресс или результат по job_id")
async def get_generation(job_id: str):
    if job_id not in tasks:
        raise HTTPException(status_code=404, detail="Job ID не найден")
    task = tasks[job_id]
    # Если задача завершилась с ошибкой, возвращаем её в JSON
    if task.get("status") == "failed":
        return {
            "job_id": job_id,
            "status": "failed",
            "progress": task.get("progress", 0.0),
            "error": task.get("error")
        }
    # Если ещё не готова
    if task["status"] != "done":
        return {"job_id": job_id, "status": task["status"], "progress": task["progress"]}
    # Готовый результат
    return {
        "job_id": job_id,
        "status": "done",
        "progress": 1.0,
        "diagram": task.get("diagram")
    }

async def run_generation(job_id: str, repo_url: str, use_gpt: bool):
    """
    Фоновая функция: клонирование → разбор → построение → сохранение в БД
    """
    temp_dir = tempfile.mkdtemp()
    parser = None
    try:
        # CLONING
        tasks[job_id]["status"] = "cloning"
        tasks[job_id]["progress"] = 0.1
        update_job_db = lambda s, p: None
        # функция обновления в БД
        def update_job_db(status: str, progress: float):
            tasks[job_id]["status"] = status
            tasks[job_id]["progress"] = progress
            try:
                with next(get_session()) as session:
                    job = session.get(Job, job_id)
                    job.status = status
                    job.progress = progress
                    job.updated_at = datetime.utcnow()
                    session.add(job)
                    session.commit()
            except SQLAlchemyError:
                pass

        # Клонируем репозиторий
        parser = RepoParser(repo_url, temp_dir) if use_gpt else StaticRepoParser(repo_url, temp_dir)
        parser.clone_repo()
        update_job_db("parsing", 0.3)

        # PARSING
        if use_gpt:
            summary = parser.summarize_all()
        else:
            graph = parser.build_graph()
            summary = {"graph": graph}
        update_job_db("building", 0.6)

        # BUILD DIAGRAM
        if use_gpt:
            diagram = DiagramBuilder(summary).build_c4()
        else:
            diagram = parser.graph_to_c4(summary["graph"])
        tasks[job_id]["diagram"] = diagram

        update_job_db("done", 1.0)

        # SAVE DIAGRAM ELEMENTS
        with next(get_session()) as session:
        # Удаляем старые элементы диаграммы для этого job_id
            session.query(DiagramElement).filter(DiagramElement.job_id == job_id).delete()
            # Вставляем новые контейнеры
            for c in diagram["containers"]:
                session.add(DiagramElement(
                    id=c['id'], job_id=job_id, type="container",
                    name=c['name'], description=c['description'], parent_id=None
                ))
            # Вставляем новые компоненты
            for comp in diagram["components"]:
                session.add(DiagramElement(
                    id=comp['id'], job_id=job_id, type="component",
                    name=comp['name'], description=comp['description'], parent_id=comp['containerId']
                ))
            # Вставляем новые связи
            for rel in diagram["relationships"]:
                rel_id = f"rel:{uuid.uuid4()}"
                session.add(DiagramElement(
                    id=rel_id, job_id=job_id, type="relationship",
                    name=None,
                    description=rel['description'], parent_id=None,
                    extra={"source": rel['source'], "destination": rel['destination']}
                ))
            session.commit()

    except Exception:
        import traceback
        tb = traceback.format_exc()
        print(f"Error in job {job_id}:\n{tb}")
        tasks[job_id]["status"] = "failed"
        tasks[job_id]["error"] = tb
    finally:
        if parser:
            parser.cleanup()
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/jobs/{job_id}/elements")
async def list_elements(job_id: uuid.UUID, session: Session = Depends(get_session)):
    elems = session.query(DiagramElement).filter_by(job_id=job_id).all()
    if not elems:
        raise HTTPException(404, detail="No elements found")
    return elems

@app.get("/elements/{element_id:path}")
async def get_element_detail(element_id: str, session: Session = Depends(get_session)):
    elem = session.get(DiagramElement, element_id)
    if not elem:
        raise HTTPException(404, detail="Element not found")
    return elem

# @app.on_event("startup")
# def on_startup():
#     # Ждём, пока база поднимется (до 30 секунд)
#     for i in range(30):
#         try:
#             init_db()
#             print("✅ Database initialized")
#             break
#         except Exception as e:
#             print(f"⏳ Waiting for DB... ({i+1}/30): {e}")
#             time.sleep(1)
#     else:
#         # Если не удалось за 30 секунд, фатально
#         raise RuntimeError("Cannot connect to the database")

@app.get("/jobs/{job_id}/diagram", response_model=DiagramResponse)
async def get_diagram(job_id: str):
    """
    Возвращает полную C4-диаграмму (containers, components, relationships)
    для указанного job_id.
    """
    task = tasks.get(job_id)
    if not task:
        raise HTTPException(404, "Job ID не найден")
    if task["status"] != "done":
        raise HTTPException(400, f"Diagram not ready: status={task['status']}")
    # diagram мы уже сохранили в tasks[job_id]['diagram']
    return task["diagram"]