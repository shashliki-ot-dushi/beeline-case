import os
import uuid
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, UUID4
from sqlalchemy import (
    create_engine, Column, String, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from dotenv import load_dotenv

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://vlad:fuck_this_case!@postgres/db"
)

# ---- DATABASE SETUP ----
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    session_token = Column(String, unique=True, index=True)
    projects = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="projects")

Base.metadata.create_all(bind=engine)

# ---- Pydantic SCHEMAS ----
class SessionResponse(BaseModel):
    session_token: str

class ProjectCreate(BaseModel):
    name: str

class ProjectResponse(BaseModel):
    id: UUID4
    name: str

# ---- AUTH & DEPENDENCIES ----
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = creds.credentials
    user = db.query(User).filter(User.session_token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

# ---- APP & ENDPOINTS ----
app = FastAPI(title="User & Project Service (Postgres + Bearer Auth)")

@app.post("/sessions", response_model=SessionResponse)
def create_session(db: Session = Depends(get_db)):
    """
    Create a new user session.
    Returns a UUID4 token to use as Bearer auth.
    """
    user_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    user = User(id=user_id, session_token=token)
    db.add(user)
    db.commit()
    return SessionResponse(session_token=token)

@app.get("/projects", response_model=List[ProjectResponse])
def list_projects(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all projects for the authenticated user.
    """
    projects = (
        db.query(Project)
        .filter(Project.owner_id == user.id)
        .all()
    )
    return [ProjectResponse(id=proj.id, name=proj.name) for proj in projects]

@app.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(
    payload: ProjectCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project for the authenticated user.
    Returns its UUID4 id.
    """
    project_id = str(uuid.uuid4())
    project = Project(
        id=project_id,
        name=payload.name,
        owner_id=user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse(id=project.id, name=project.name)

@app.delete("/projects/{project_id}", status_code=204)
def delete_project(
    project_id: UUID4,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete one of the authenticated user's projects.
    """
    project = (
        db.query(Project)
        .filter(
            Project.id == str(project_id),
            Project.owner_id == user.id
        )
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return Response(status_code=204)
