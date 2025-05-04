from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import Column
from sqlalchemy import JSON
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import os

# URL из .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Создаём движок и мигрируем
engine = create_engine(
    DATABASE_URL,
    echo=False,  # True для SQL-логов
    connect_args={}
)

class Job(SQLModel, table=True):
    __tablename__ = "job"
    job_id: UUID = Field(primary_key=True)
    repo_url: str
    use_gpt: bool
    status: str
    progress: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DiagramElement(SQLModel, table=True):
    __tablename__ = "diagram_elements"
    job_id: UUID = Field(foreign_key="job.job_id", primary_key=True)
    id: str       = Field(primary_key=True)
    type: str
    name: Optional[str]
    description: Optional[str]
    parent_id: Optional[str]
    extra: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON, nullable=True))

# Инициализация БД при старте
def init_db():
    SQLModel.metadata.create_all(engine)

# Dependency для FastAPI
def get_session():
    with Session(engine) as session:
        yield session