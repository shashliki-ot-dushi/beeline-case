# service/main.py
import os, tempfile, shutil
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from autodoc.generator import collect_docs

app = FastAPI()
REPO_URL = os.getenv("REPO_URL")  # напр. https://github.com/Happ1S/autodoc.git
TARGET_MD = "/data/DOCUMENTATION.md"

@app.post("/generate")
def generate(ref: str | None = None):
    if not REPO_URL:
        raise HTTPException(500, "REPO_URL env var not set")
    tmp = tempfile.mkdtemp()
    try:
        # клонит нужную ветку/коммит
        cmd = ["git", "clone", "--depth", "1"]
        if ref:
            cmd += ["--branch", ref]
        cmd += [REPO_URL, tmp]
        os.system(" ".join(cmd))
        collect_docs(tmp, TARGET_MD)
        size = os.path.getsize(TARGET_MD)
        return {"status": "ok", "bytes": size}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

@app.get("/download")
def download():
    if not os.path.exists(TARGET_MD):
        raise HTTPException(404, "Run /generate first")
    return FileResponse(TARGET_MD, media_type="text/markdown", filename="DOCUMENTATION.md")
