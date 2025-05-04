import uuid
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session


from common.auth.dependency import security
from common.database.dependency import get_db
from common.schemas.user import User
from common.schemas.project import Project

from fastapi.middleware.cors import CORSMiddleware

# ---- APP & ENDPOINTS ----
app = FastAPI(title="User & Project Service (Postgres + Bearer Auth)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Pydantic SCHEMAS ----
class SessionResponse(BaseModel):
    session_token: str

class ProjectCreate(BaseModel):
    repo_url: str

class ProjectResponse(BaseModel):
    id: uuid.UUID
    repo_url: str

# ---- AUTH & DEPENDENCIES ----

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = creds.credentials
    user = db.query(User).filter(User.session_token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

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
    return [ProjectResponse(id=proj.id, repo_url=proj.name) for proj in projects]

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
        name=payload.repo_url,
        owner_id=user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse(id=project.id, repo_url=project.name)

@app.delete("/projects/{project_id}", status_code=204)
def delete_project(
    project_id: uuid.UUID,
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
