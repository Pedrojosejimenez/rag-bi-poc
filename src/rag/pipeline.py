"""
Pipeline RAG:
1) Recupera top_k chunks por similitud semántica.
2) Llama al generador LLM local (Ollama) para sintetizar respuesta con citas.
3) Fallback a modo 'stub' extractivo si no hay Ollama.

La función pública principal es answer(query: str) -> dict
"""

from typing import Dict, List
from pathlib import Path
import numpy as np
import httpx
from .embeddings import Embeddings
from .vectorstore import build_store
from ..app.config import settings

# Instancias únicas
EMB = Embeddings(settings.embeddings_model)
VEC = build_store(settings.rag_backend, dim=EMB.encode(["x"]).shape[1], processed_dir=settings.processed_dir)

def _retrieve(query: str, top_k: int = 5) -> List[Dict]:
    qv = EMB.encode([query])
    hits = VEC.search(qv, top_k=top_k)
    # normalizamos estructura
    passages = []
    for score, m in hits:
        passages.append({
            "score": score,
            "text": m["text"],
            "source": m.get("source"),
            "chunk_id": m.get("chunk_id")
        })
    return passages

def _generate_with_ollama(query: str, passages: List[Dict]) -> str:
    prompt = (
        "Eres un sistema que responde con precisión usando SOLO los pasajes proporcionados.\n"
        "Si falta información, admite la incertidumbre. Cita las fuentes al final como [n].\n\n"
        "Pregunta:\n"
        f"{query}\n\n"
        "Pasajes:\n"
    )
    for i, p in enumerate(passages, 1):
        prompt += f"[{i}] (source: {p['source']} chunk:{p['chunk_id']}) {p['text']}\n\n"

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(f"{settings.ollama_base_url}/api/generate", json=payload)
            r.raise_for_status()
            data = r.json()
            return data.get("response", "").strip()
    except Exception:
        # fallback en caso de que Ollama no esté levantado
        return ""

def _generate_stub(query: str, passages: List[Dict]) -> str:
    # Estrategia extractiva: selecciona 2-3 pasajes más relevantes y los presenta con contexto y citas.
    selected = passages[:3]
    body = []
    for i, p in enumerate(selected, 1):
        body.append(f"- Evidencia {i}: {p['text'][:500]} [...] (fuente: {p['source']}, chunk {p['chunk_id']})")
    return (
        "Respuesta basada en evidencia local (modo stub, sin LLM generativo):\n"
        + "\n".join(body)
        + "\nConclusión: La respuesta se ha construido extrayendo los fragmentos más relevantes de tus documentos."
    )

def answer(query: str, top_k: int = 5) -> Dict:
    passages = _retrieve(query, top_k=top_k)
    if settings.generator_mode.lower() == "ollama":
        out = _generate_with_ollama(query, passages)
        if not out:
            out = _generate_stub(query, passages)
            mode = "stub"
        else:
            mode = "ollama"
    else:
        out = _generate_stub(query, passages)
        mode = "stub"

    citations = []
    for i, p in enumerate(passages, 1):
        citations.append({"id": i, "source": p["source"], "chunk_id": p["chunk_id"], "score": p["score"]})

    return {
        "query": query,
        "answer": out,
        "mode": mode,
        "citations": citations
    }
