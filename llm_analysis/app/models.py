from pydantic import BaseModel
from typing import List

class RepoRequest(BaseModel):
    repo_url: str

class ContainerModel(BaseModel):
    id: str
    name: str
    description: str

class ComponentModel(BaseModel):
    id: str
    name: str
    description: str
    containerId: str

class RelationshipModel(BaseModel):
    source: str
    destination: str
    description: str

class DiagramResponse(BaseModel):
    containers: List[ContainerModel]
    components: List[ComponentModel]
    relationships: List[RelationshipModel]
