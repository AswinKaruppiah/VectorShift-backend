from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Ping": "Pong"}

class Node(BaseModel):
    id: str

    class Config:
        extra = "allow"


class Edge(BaseModel):
    source: str
    target: str

    class Config:
        extra = "allow"  


class PipelineData(BaseModel):
    pipeline: str | None = None
    nodes: List[Node]
    edges: List[Edge]

def is_valid_pipeline(nodes, edges):

   # ❌ No nodes → invalid pipeline
    if not nodes:
        return False

    if len(nodes) == 1 and not edges:
        return True

    graph = {n.id: [] for n in nodes}
    reverse_graph = {n.id: [] for n in nodes}

    for e in edges:
        graph[e.source].append(e.target)
        reverse_graph[e.target].append(e.source)

    visited = set()
    path = set()

    def dfs_cycle(node):
        if node in path:
            return True
        if node in visited:
            return False

        visited.add(node)
        path.add(node)

        for nxt in graph[node]:
            if dfs_cycle(nxt):
                return True

        path.remove(node)
        return False

    for n in graph:
        if n not in visited:
            if dfs_cycle(n):
                return False  

    seen = set()

    def dfs_connected(node):
        if node in seen:
            return
        seen.add(node)

        for nxt in graph[node] + reverse_graph[node]:
            dfs_connected(nxt)

    start_node = nodes[0].id
    dfs_connected(start_node)

    if len(seen) != len(nodes):
        return False  

    return True


@app.post("/pipelines/parse")
def parse_pipeline(data: PipelineData):
    num_nodes = len(data.nodes)
    num_edges = len(data.edges)
    is_dag = is_valid_pipeline(data.nodes, data.edges)
    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "is_dag": is_dag
    }
