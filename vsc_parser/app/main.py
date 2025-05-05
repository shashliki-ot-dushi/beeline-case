import os, tempfile, shutil
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from minio import Minio

from git import Repo
import networkx as nx

from sqlalchemy.orm import Session

from common.auth.policy import security
from common.database.dependency import get_db
from common.auth.dependency import get_current_user
from common.schemas.user import User
from common.schemas.project import Project

from app.code_parser import (
    ingest_code,
    ingest_tests,
    ingest_docs,
    ingest_config,
    ingest_vcs,
)
from app.adapters.cpp_adapter import CppAdapter
from app.adapters.python_adapter import PythonAdapter

app = FastAPI()

G = nx.MultiDiGraph()


@app.post("/parse/{project_id}")
def parse_project(
    project_id: str,
    db: Session = Depends(get_db),
    user: User  = Depends(get_current_user),
):
    project: Project = (
        db.query(Project)
          .filter(Project.id == str(project_id), Project.owner_id == user.id)
          .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    repo_url = project.name
    tmpdir = tempfile.mkdtemp()

    try:
        BASE = Path(tmpdir)
        Repo.clone_from(repo_url, BASE)

        adapter = PythonAdapter()
        ingest_code(BASE, adapter, project.id)
        ingest_tests(BASE, project.id)
        ingest_docs(BASE, project.id)
        ingest_config(BASE, project.id)
        ingest_vcs(BASE, project.id)  # Optionally enable

        return {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
        }

    finally:
        shutil.rmtree(tmpdir)