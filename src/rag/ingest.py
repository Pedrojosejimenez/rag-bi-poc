"""
Ingesta:
- Lee PDF/MD/TXT en data/raw
- Chunquea (500-800 "tokens" aproximados por palabras)
- Calcula embeddings y actualiza el índice vectorial (FAISS o Qdrant)
- Guarda artefactos en data/processed

Idempotente: puede ejecutarse múltiples veces sin romper el índice.
"""

from pathlib import Path
from typing import List, Dict
from ..app.config import settings
from .chunk import load_and_chunk_file
from .embeddings import Embeddings
from .vectorstore import build_store
import pandas as pd
import numpy as np

def discover_files(raw_dir: Path) -> List[Path]:
    exts = {".pdf", ".md", ".markdown", ".txt"}
    return [p for p in raw_dir.glob("*") if p.suffix.lower() in exts]

def run_ingest() -> None:
    raw_dir = settings.data_dir / "raw"
    processed_dir = settings.processed_dir
    processed_dir.mkdir(parents=True, exist_ok=True)

    files = discover_files(raw_dir)
    if not files:
        print(f"No se encontraron documentos en {raw_dir}. Añade PDF/MD/TXT y vuelve a ejecutar.")
        return

    # Carga/Chunk
    all_chunks: List[Dict] = []
    for f in files:
        chunks = load_and_chunk_file(
            f,
            target_tokens=settings.chunk_target_tokens,
            overlap_tokens=settings.chunk_overlap_tokens
        )
        all_chunks.extend(chunks)

    if not all_chunks:
        print("No se generaron chunks. Revisa los documentos.")
        return

    texts = [c["text"] for c in all_chunks]
    metas = [{"source": c["metadata"]["source"], "chunk_id": c["metadata"]["chunk_id"]} for c in all_chunks]

    # Embeddings
    EMB = Embeddings(settings.embeddings_model)
    vecs = EMB.encode(texts)

    # Vector store
    store = build_store(settings.rag_backend, dim=vecs.shape[1], processed_dir=processed_dir)
    store.add(texts, metas, vecs)

    # Guardamos una tabla auxiliar para inspección
    df = pd.DataFrame({"text": texts, "source": [m["source"] for m in metas], "chunk_id": [m["chunk_id"] for m in metas]})
    df.to_parquet(processed_dir / "chunks.parquet", index=False)

    print(f"Ingesta completada. Chunks: {len(all_chunks)}. Backend: {settings.rag_backend}. Artefactos en {processed_dir}")

if __name__ == "__main__":
    run_ingest()
