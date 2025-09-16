"""
Chunking sencillo y robusto.
- Extrae texto de PDF y Markdown.
- Limpia espacios y normaliza.
- Divide por ~tokens usando aproximación por palabras (evita dependencias complejas).
- Controla solape entre chunks para preservar contexto (ventana deslizante).
"""

from pathlib import Path
from typing import List, Dict
from pypdf import PdfReader
from markdown_it import MarkdownIt
import re

def read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)

def read_md(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    # Render duro -> solo texto plano desde markdown
    md = MarkdownIt()
    tokens = md.parse(text)
    content = []
    for tok in tokens:
        if tok.content:
            content.append(tok.content)
    return "\n".join(content)

def clean_text(s: str) -> str:
    s = s.replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def word_tokenize(s: str) -> List[str]:
    # Suficiente para chunking. Evitamos NLTK pesada y aseguramos portabilidad.
    return re.findall(r"\S+", s)

def chunk_text(
    text: str,
    target_tokens: int = 700,
    overlap_tokens: int = 120,
    metadata: Dict = None,
) -> List[Dict]:
    """
    Devuelve lista de dicts: { 'text': str, 'metadata': {..., 'chunk_id': int} }
    """
    words = word_tokenize(text)
    if not words:
        return []
    chunks = []
    start = 0
    chunk_id = 0
    step = max(target_tokens - overlap_tokens, 1)

    while start < len(words):
        end = min(start + target_tokens, len(words))
        piece = " ".join(words[start:end])
        chunks.append({
            "text": piece,
            "metadata": {**(metadata or {}), "chunk_id": chunk_id}
        })
        chunk_id += 1
        start += step
    return chunks

def load_and_chunk_file(path: Path, target_tokens=700, overlap_tokens=120) -> List[Dict]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        raw = read_pdf(path)
    elif suffix in {".md", ".markdown"}:
        raw = read_md(path)
    else:
        # Otros formatos: tratamos como texto plano
        raw = path.read_text(encoding="utf-8", errors="ignore")
    raw = clean_text(raw)
    return chunk_text(raw, target_tokens, overlap_tokens, metadata={"source": str(path)})

