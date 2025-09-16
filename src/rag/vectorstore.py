"""
Almacenamiento vectorial local:
- FAISS (por defecto, sin red)
- Qdrant (opcional, vía docker-compose)
Ambos ofrecen: add(texts, metadatas), search(query_vec, top_k) -> (scores, payloads)
"""

from typing import List, Dict, Tuple
import numpy as np
from pathlib import Path

from .embeddings import Embeddings

# FAISS
import faiss
import pickle

# Qdrant opcional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter

class BaseVectorStore:
    def add(self, texts: List[str], metadatas: List[Dict]) -> None: ...
    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[float, Dict]]: ...

class FaissStore(BaseVectorStore):
    def __init__(self, dim: int, index_path: Path, meta_path: Path):
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path
        if index_path.exists():
            self.index = faiss.read_index(str(index_path))
            self.metadatas: List[Dict] = pickle.loads(meta_path.read_bytes())
        else:
            self.index = faiss.IndexFlatIP(dim)  # IP requiere embeddings normalizados
            self.metadatas = []

    def add(self, texts: List[str], metadatas: List[Dict], embeddings: np.ndarray) -> None:
        assert embeddings.shape[1] == self.dim
        self.index.add(embeddings)
        for i, m in enumerate(metadatas):
            self.metadatas.append({**m, "text": texts[i]})
        faiss.write_index(self.index, str(self.index_path))
        self.meta_path.write_bytes(pickle.dumps(self.metadatas))

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[float, Dict]]:
        D, I = self.index.search(query_vec, top_k)
        out = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.metadatas):
                continue
            m = self.metadatas[idx]
            out.append((float(score), m))
        return out

class QdrantStore(BaseVectorStore):
    def __init__(self, collection: str = "rag_chunks", host="127.0.0.1", port=6333, dim: int = 384):
        self.client = QdrantClient(host=host, port=port)
        self.collection = collection
        # Crea colección si no existe
        if collection not in [c.name for c in self.client.get_collections().collections]:
            self.client.recreate_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
            )

    def add(self, texts: List[str], metadatas: List[Dict], embeddings: np.ndarray) -> None:
        points = []
        for i in range(len(texts)):
            payload = {**metadatas[i], "text": texts[i]}
            points.append(PointStruct(id=None, vector=embeddings[i].tolist(), payload=payload))
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[float, Dict]]:
        res = self.client.search(
            collection_name=self.collection,
            query_vector=query_vec[0].tolist(),
            limit=top_k
        )
        out = []
        for p in res:
            out.append((1 - float(p.score), p.payload))  # COSINE -> 1 - score como "distancia"
        return out

def build_store(backend: str, dim: int, processed_dir: Path):
    if backend.lower() == "qdrant":
        return QdrantStore(dim=dim)
    # FAISS por defecto
    return FaissStore(dim=dim,
                      index_path=processed_dir / "faiss.index",
                      meta_path=processed_dir / "faiss_meta.pkl")
