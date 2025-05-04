import git
import tempfile
from fastapi import FastAPI, HTTPException
from app.models import RepoRequest, DiagramResponse
from app.parser import RepoParser
from app.diagram import DiagramBuilder
from app.static_analyzer import StaticRepoParser


app = FastAPI(title="C4 Generator")

@app.post("/generate-diagram", response_model=DiagramResponse)
async def generate_diagram(req: RepoRequest):
    temp_dir = tempfile.mkdtemp()
    #parser = RepoParser(req.repo_url, temp_dir)
    parser = StaticRepoParser(req.repo_url, temp_dir)
    try:
        #parser.clone_repo()
        #summary = parser.summarize_all()
        #diagram = DiagramBuilder(summary).build_c4()
        parser.clone_repo()
        graph = parser.build_graph()
        diagram = parser.graph_to_c4(graph)
        return diagram
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        parser.cleanup()
