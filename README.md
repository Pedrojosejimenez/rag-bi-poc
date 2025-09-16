# POC RAG + Business Intelligence (100 % local y gratuito)

Esta prueba de concepto combina **RAG** sobre documentos locales con un **dashboard de BI** en Streamlit y una **API HTTP** con FastAPI. Todo se ejecuta en tu equipo sin claves de pago.

## Arquitectura

[PDF/MD/TXT] --> Ingesta -> Chunking -> Embeddings -> Vector Store (FAISS|Qdrant)
|
v
Pipeline RAG ----> (Ollama LLM) -> Respuesta con citas
| ^
v |
FastAPI /ask endpoint Fallback modo "stub"
|
v
Streamlit Dashboard (KPIs + RAG)


## Requisitos

- Python 3.11 (Windows, Linux, WSL).
- **Opcional**: Docker si usas Qdrant.
- **Opcional**: [Ollama](https://ollama.com) y un modelo gratuito (`ollama pull llama3` o `ollama pull mistral`).

## Instalación

```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
# venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

Copia .env.example a .env si quieres cambiar opciones. Por defecto usamos FAISS y GENERATOR_MODE=ollama. Si no tienes Ollama, pon GENERATOR_MODE=stub.

Ingesta de documentos

Coloca tus PDF/MD/TXT en data/raw/. Incluimos sample.md. Ejecuta:

python src/rag/ingest.py


Esto crea data/processed/faiss.index y faiss_meta.pkl o envía los vectores a Qdrant si activas ese backend.

Usar Qdrant (opcional)
docker-compose up -d
# y en .env:
# RAG_BACKEND=qdrant

API HTTP (FastAPI)

Arranque:

uvicorn src.app.server:app --reload


Prueba:

curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" \
  -d '{"query":"¿Qué contiene el documento de ejemplo?","top_k":5}'

Dashboard BI (Streamlit)
streamlit run src/bi/dashboard.py


Pestañas:

Ventas: KPIs y series temporales.

Soporte: métricas de tickets y tiempos.

RAG: formulario para consultar vía API o local.

Modelos y costes

Embeddings: all-MiniLM-L6-v2 (gratuito).

Generación: Ollama con llama3 o mistral (gratuitos). Si no lo tienes, usa GENERATOR_MODE=stub, que ofrece respuesta extractiva sin LLM.

Subir a GitHub
git init
git add .
git commit -m "POC RAG+BI 100% local"
git branch -M main
git remote add origin https://github.com/<tu_usuario>/rag_bi_poc.git
git push -u origin main

Resolución de errores comunes

Ollama no responde: pon GENERATOR_MODE=stub en .env o arranca ollama serve y ollama pull llama3.

FAISS en Windows: este repo fija faiss-cpu==1.8.0.post1, compatible en Python 3.11. Asegúrate de tener pip actualizado.

Qdrant puerto en uso: cambia puertos en docker-compose.yml.

Sin documentos: coloca archivos en data/raw y relanza ingest.py.

Tests

Ejecuta:

make test
# o
GENERATOR_MODE=stub pytest -q

Estructura de carpetas
src/
  rag/      # Ingesta, chunking, embeddings, vector store, pipeline
  app/      # FastAPI + rutas
  bi/       # Datos de ejemplo y dashboard Streamlit
data/
  raw/      # Tus documentos
  processed/# Índices y artefactos
  examples/ # CSV de demo + golden questions

Licencia

MIT.


---

# Checklist de verificación

- [x] Instalación con `requirements.txt` versiones fijas.
- [x] Ingesta reproducible: `python src/rag/ingest.py`.
- [x] API: `uvicorn src.app.server:app --reload` responde en `/health` y `/ask`.
- [x] Dashboard: `streamlit run src/bi/dashboard.py`.
- [x] Datos ejemplo autogenerados si faltan.
- [x] RAG con FAISS por defecto y Qdrant opcional en Docker.
- [x] Generación con Ollama o fallback `stub` sin coste.
- [x] Tests `pytest` pasan en modo `stub`.
- [x] Makefile con tareas idempotentes.
- [x] Portabilidad Windows/Linux/WSL.
- [x] LICENSE MIT incluida.

---

# Auditoría de requisitos y dónde se cumplen

1) **Árbol, código, comandos, README, checklist** → entregados arriba.  
2) **Sin TODO ni huecos** → no hay marcadores TODO.  
3) **`requirements.txt` con versiones fijas** → incluido.  
4) **Scripts y Makefile idempotentes** → `Makefile` objetivos `ingest`, `api`, `ui`, `test`.  
5) **Portabilidad** → dependencias puras Python; FAISS CPU; instrucciones Windows/WSL.  
6) **MIT** → `LICENSE`.  
7) **RAG local sobre `data/raw` con citas** → `pipeline.answer` devuelve `citations`; `ingest.py` y `chunk.py`.  
8) **Dashboard BI con Streamlit** → `src/bi/dashboard.py`, KPIs y gráficos, pestaña RAG.  
9) **API HTTP FastAPI** → `src/app/server.py`, `src/app/routes_rag.py` (`/health`, `/ask`).  
10) **Tecnologías** → sentence-transformers, faiss, qdrant opcional, streamlit, fastapi, pydantic, pytest, matplotlib, duckdb.  
11) **Modelos gratuitos** → `EMBEDDINGS_MODEL` y `OLLAMA_MODEL` documentados, fallback stub.  
12) **Ingesta 500–800 tokens** → `chunk.py` con ~700 palabras y solape, configurable en `.env`.  
13) **Tests** → `tests/test_rag.py`, `tests/test_bi.py`.  
14) **Datos de ejemplo** → `src/bi/load_data.py` autogenera `sales.csv`, `support_tickets.csv`, `golden_questions.jsonl`.  
15) **README detallado** → incluido con diagrama ASCII, pasos, GitHub, troubleshooting.  

Todo es 100 % software libre o gratuito y ejecutable de principio a fin sin depender de servicios 
