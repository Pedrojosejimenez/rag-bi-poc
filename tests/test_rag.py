from pathlib import Path
from src.rag.ingest import run_ingest
from src.rag.pipeline import answer
from src.app.config import settings

def test_ingest_and_answer(tmp_path, monkeypatch):
    # Preparar entorno de datos temporal
    data_dir = tmp_path / "data"
    raw = data_dir / "raw"
    proc = data_dir / "processed"
    raw.mkdir(parents=True)
    proc.mkdir(parents=True)

    # Doc simple
    p = raw / "doc.md"
    p.write_text("RAG de prueba. Esta es una POC. Contiene información de ejemplo.", encoding="utf-8")

    # Redirigimos rutas
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("PROCESSED_DIR", str(proc))
    from importlib import reload
    import src.app.config as cfg
    reload(cfg)  # recargar settings
    # Ejecutar ingesta
    run_ingest()
    # Consultar
    res = answer("¿Qué es esta POC?")
    assert "POC" in res["answer"] or "evidencia" in res["answer"].lower()
    assert len(res["citations"]) >= 1
