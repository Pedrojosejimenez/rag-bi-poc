"""
Generación/carga de datos de ejemplo para BI:
- sales.csv: 24 meses, 3 regiones, 3 productos, ventas y coste.
- support_tickets.csv: tickets con prioridad y tiempo de resolución.

Si los ficheros no existen, se crean determinísticamente.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from ..app.config import settings

EX_DIR = settings.data_dir / "examples"
EX_DIR.mkdir(parents=True, exist_ok=True)

SALES = EX_DIR / "sales.csv"
SUPPORT = EX_DIR / "support_tickets.csv"
GOLDEN = EX_DIR / "golden_questions.jsonl"

def ensure_sales():
    if SALES.exists():
        return pd.read_csv(SALES, parse_dates=["date"])
    # 24 meses desde hoy hacia atrás
    periods = 24
    base = pd.date_range(end=pd.Timestamp.today().normalize(), periods=periods, freq="MS")
    regions = ["Norte", "Centro", "Sur"]
    products = ["Alpha", "Beta", "Gamma"]
    rows = []
    rng = np.random.default_rng(42)
    for d in base:
        for r in regions:
            for p in products:
                sales = max(1000, int(rng.normal(5000, 1200)))
                cost = int(sales * rng.uniform(0.45, 0.7))
                rows.append([d, r, p, sales, cost])
    df = pd.DataFrame(rows, columns=["date", "region", "product", "sales", "cost"])
    df.to_csv(SALES, index=False)
    return df

def ensure_support():
    if SUPPORT.exists():
        return pd.read_csv(SUPPORT, parse_dates=["created_at", "resolved_at"])
    n = 600
    rng = np.random.default_rng(7)
    start = pd.Timestamp.today().normalize() - pd.offsets.MonthBegin(24)
    created = [start + pd.Timedelta(days=int(rng.integers(0, 730))) for _ in range(n)]
    priorities = rng.choice(["low", "medium", "high"], size=n, p=[0.5, 0.35, 0.15])
    resolve_hours = rng.integers(2, 120, size=n)
    resolved = [c + pd.Timedelta(hours=int(h)) for c, h in zip(created, resolve_hours)]
    df = pd.DataFrame({"created_at": created, "resolved_at": resolved, "priority": priorities})
    df["resolution_hours"] = (df["resolved_at"] - df["created_at"]).dt.total_seconds() / 3600.0
    df.to_csv(SUPPORT, index=False)
    return df

def ensure_golden():
    if GOLDEN.exists():
        return
    items = [
        {"question": "¿Cuál es el tema principal del documento sample.md?", "expected_contains": "POC"},
        {"question": "Resume el PDF de ejemplo en dos frases.", "expected_contains": "ejemplo"}
    ]
    with open(GOLDEN, "w", encoding="utf-8") as f:
        for it in items:
            f.write(f'{it}\n')

def load_all():
    sales = ensure_sales()
    support = ensure_support()
    ensure_golden()
    return sales, support
