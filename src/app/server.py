"""
Servidor FastAPI.
Arranque local: uvicorn src.app.server:app --reload
"""

# src/app/server.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from .routes_rag import router as rag_router

# routes_agent es opcional: si no existe, la API sigue funcionando
try:
    from .routes_agent import router as agent_router
    HAS_AGENT = True
except Exception:
    HAS_AGENT = False

app = FastAPI(title="RAG+BI POC", version="1.0.0")

# registra rutas
app.include_router(rag_router, prefix="")
if HAS_AGENT:
    app.include_router(agent_router, prefix="")

# raíz → docs
@app.get("/")
def root():
    return RedirectResponse(url="/docs")
