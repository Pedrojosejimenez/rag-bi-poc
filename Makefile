PY=python
PIP=pip

.PHONY: help setup venv install ingest api ui test qdrant-up qdrant-down clean

help:
	@echo "Objetivos: setup | install | ingest | api | ui | test | qdrant-up | qdrant-down | clean"

setup:
	$(PY) -m venv venv && \
	. venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || true && \
	$(PIP) install --upgrade pip && pip install -r requirements.txt

install:
	$(PIP) install -r requirements.txt

ingest:
	$(PY) -m src/rag/ingest.py

api:
	uvicorn src.app.server:app --reload

ui:
	streamlit run src/bi/dashboard.py

test:
	GENERATOR_MODE=stub pytest -q

qdrant-up:
	docker-compose up -d

qdrant-down:
	docker-compose down

clean:
	rm -rf data/processed/*.pkl data/processed/*.faiss .pytest_cache __pycache__
