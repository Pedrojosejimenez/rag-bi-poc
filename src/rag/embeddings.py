"""
Embeddings con sentence-transformers (gratuito).
Modelo por defecto: all-MiniLM-L6-v2 (rápido y ligero).
"""

from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

class Embeddings:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        # Descarga la primera vez y cachea localmente (~80MB)
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]) -> np.ndarray:
        # Normalizamos float32 para compatibilidad FAISS
        vecs = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return vecs.astype("float32")
