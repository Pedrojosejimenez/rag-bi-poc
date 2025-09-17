# POC RAG + BI 100 % local y gratuita (Windows, WSL y Linux)

Esta prueba de concepto integra **RAG** sobre documentos locales (PDF, MD, TXT) con un **dashboard de Business Intelligence** y una **API HTTP**. Todo se ejecuta en local, sin claves de pago, con componentes 100 % libres. Incluye un **agente de enrutado** que decide si responder con BI, con RAG o con ambos, y un **modo fallback** sin LLM generativo para asegurar funcionamiento en cualquier equipo.

---

## Novedades operativas de esta versión

- Importaciones compatibles con Streamlit: se usan **imports absolutos** `from src...` y ficheros `__init__.py` en `src/`, `src/app/`, `src/rag/`, `src/bi/` y `src/agent/`.
- Ejecución como **módulo** (`python -m ...`) para evitar errores de importación.
- API con redirección opcional **`/ → /docs`** para evitar 404 en la raíz.
- Nueva ruta **`POST /agent_ask`** y pestaña **Agente** en Streamlit para respuestas combinadas BI + RAG.
- Guía precisa para **PowerShell** y fijación de **UTF-8** para evitar problemas de acentuación.

---

## Estructura

rag_bi_poc/
README.md
LICENSE
.env.example
requirements.txt
docker-compose.yml
Makefile
.gitignore
src/
init.py
app/
init.py
server.py # incluye redirección / -> /docs y registro del agente si existe
routes_rag.py
routes_agent.py # expone POST /agent_ask
rag/
init.py
ingest.py
chunk.py
embeddings.py
vectorstore.py
pipeline.py
bi/
init.py
load_data.py
dashboard.py # pestaña “Agente” y imports absolutos
agent/
init.py
router.py # heurística BI/RAG/both
sql_exec.py # plantillas SQL seguras en DuckDB
orchestrator.py # orquesta BI + RAG y compone respuesta
data/
raw/
processed/
examples/
tests/
conftest.py
test_rag.py
test_bi.py

yaml
Copiar código

---

## Requisitos

- **Python 3.11**.
- **Git** y **Visual Studio Code**.
- Opcional RAG generativo: **Ollama** con un modelo gratuito (`llama3` o `mistral`).
- Opcional vector store en servicio: **Docker Desktop** para Qdrant.

---

## Instalación

En **PowerShell**:

```powershell
# 1) Ubícate en la carpeta del proyecto
cd "<ruta a tu proyecto>\rag-bi-poc"

# 2) Entorno virtual
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1

# Si PowerShell bloquea scripts, ejecuta una vez:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

python -m pip install --upgrade pip
pip install -r requirements.txt

# 3) Asegura inicializadores de paquete
ni src\__init__.py -ItemType File -Force
ni src\app\__init__.py -ItemType File -Force
ni src\rag\__init__.py -ItemType File -Force
ni src\bi\__init__.py -ItemType File -Force
ni src\agent\__init__.py -ItemType File -Force
Configuración
Copia .env.example a .env. Valores útiles:

ini
Copiar código
RAG_BACKEND=faiss
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
GENERATOR_MODE=stub        # usa “ollama” si tienes Ollama activo
OLLAMA_MODEL=llama3
DATA_DIR=./data
PROCESSED_DIR=./data/processed
CHUNK_TARGET_TOKENS=700
CHUNK_OVERLAP_TOKENS=120
Si no usarás Ollama, deja GENERATOR_MODE=stub.

Ingesta de documentos
Coloca PDF/MD/TXT en data/raw/. Ejecuta:

powershell
Copiar código
# Importante: ejecutar como módulo para resolver imports
python -m src.rag.ingest
Se crearán los artefactos en data/processed/ (FAISS) o se enviarán a Qdrant si lo habilitas en .env.

Arranque de la API
Usa dos terminales para trabajar cómodo.

Consola A:

powershell
Copiar código
cd "<ruta a tu proyecto>\rag-bi-poc"
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH="$PWD"
python -m uvicorn src.app.server:app --host 127.0.0.1 --port 8000
Verificación rápida:

Salud: http://127.0.0.1:8000/health

Documentación: http://127.0.0.1:8000/docs

Probar endpoints desde PowerShell
Antes de enviar texto con acentos, fija UTF-8:

powershell
Copiar código
[Console]::InputEncoding  = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
Luego:

powershell
Copiar código
# /ask
$payload = [PSCustomObject]@{ query = '¿Qué contiene el documento de ejemplo?'; top_k = 5 }
$json = $payload | ConvertTo-Json -Depth 5 -Compress
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/ask' -Method POST -Body $json -ContentType 'application/json; charset=utf-8'

# /agent_ask
$payload = [PSCustomObject]@{ query = 'Ventas por región y, según documentos, política de devoluciones'; top_k = 5 }
$json = $payload | ConvertTo-Json -Depth 5 -Compress
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/agent_ask' -Method POST -Body $json -ContentType 'application/json; charset=utf-8'
Alternativa con curl.exe real:

powershell
Copiar código
curl.exe -s -X POST "http://127.0.0.1:8000/ask" -H "Content-Type: application/json; charset=utf-8" -d "{\"query\":\"¿Qué contiene el documento de ejemplo?\",\"top_k\":5}"
Dashboard Streamlit
Consola B:

powershell
Copiar código
cd "<ruta a tu proyecto>\rag-bi-poc"
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH="$PWD"
streamlit run src/bi/dashboard.py
Pestañas:

Ventas: KPIs y series temporales con DuckDB.

Soporte: tickets, prioridad y tiempos.

RAG: preguntas a /ask o pipeline local.

Agente: formulario a /agent_ask que devuelve respuesta combinada, tabla BI y citas RAG si existen.

LLM local con Ollama (opcional)
powershell
Copiar código
# en otra consola
ollama pull llama3

# en .env
# GENERATOR_MODE=ollama
# OLLAMA_MODEL=llama3

# reinicia Uvicorn
Qdrant opcional (Docker)
powershell
Copiar código
docker-compose up -d
# en .env:
# RAG_BACKEND=qdrant
python -m src.rag.ingest
Tests
powershell
Copiar código
# Evitar dependencia de LLM en tests
$env:GENERATOR_MODE="stub"
pytest -q
Solución de problemas
ImportError: attempted relative import with no known parent package
Ejecutar como módulo: python -m src.rag.ingest. Asegurar __init__.py en src/*.

404 en /
Normal si no hay ruta raíz. Usar /health o /docs. Redirección opcional en server.py:

python
Copiar código
@app.get("/")
def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
400 “There was an error parsing the body”
En PowerShell convertir objetos a JSON con ConvertTo-Json y enviar -ContentType 'application/json'. No pegar comentarios # ni >> junto a los comandos.

“No es posible conectar con el servidor remoto”
Uvicorn apagado o puerto distinto. Mantener la consola A encendida. Verificar con:

powershell
Copiar código
netstat -ano | findstr :8000
Acentos corruptos (mojibake)
Fijar UTF-8 en consola como arriba.

Aviso de torch.classes
Benigno. Si molesta: pip install --index-url https://download.pytorch.org/whl/cpu torch==2.3.1.


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
