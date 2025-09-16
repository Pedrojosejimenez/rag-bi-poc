"""
Config centralizada. Lee .env y ofrece valores tipados.
Diseño: pydantic + dotenv. Evita claves de pago. Todo local.
"""

from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

class Settings(BaseModel):
    rag_backend: str = Field(default=os.getenv("RAG_BACKEND", "faiss"))
    embeddings_model: str = Field(default=os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    ollama_base_url: str = Field(default=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    ollama_model: str = Field(default=os.getenv("OLLAMA_MODEL", "llama3"))
    generator_mode: str = Field(default=os.getenv("GENERATOR_MODE", "ollama"))  # ollama|stub
    data_dir: Path = Field(default=Path(os.getenv("DATA_DIR", "./data")))
    processed_dir: Path = Field(default=Path(os.getenv("PROCESSED_DIR", "./data/processed")))
    chunk_target_tokens: int = Field(default=int(os.getenv("CHUNK_TARGET_TOKENS", "700")))
    chunk_overlap_tokens: int = Field(default=int(os.getenv("CHUNK_OVERLAP_TOKENS", "120")))

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "raw").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "processed").mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_dirs()
