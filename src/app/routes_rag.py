"""
Rutas de API para el RAG: /health y /ask
"""

from fastapi import APIRouter
from pydantic import BaseModel
from ..rag.pipeline import answer

router = APIRouter()

class AskRequest(BaseModel):
    query: str
    top_k: int = 5

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/ask")
def ask(req: AskRequest):
    res = answer(req.query, top_k=req.top_k)
    return res
