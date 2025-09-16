"""
Dashboard Streamlit:
- KPIs y gráficos de ventas y soporte (DuckDB para consultas simples).
- Pestaña RAG con formulario que llama a la API FastAPI local o al pipeline directo.
- Muestra pasajes recuperados y tiempos aproximados.

Ejecución: streamlit run src/bi/dashboard.py
"""

import streamlit as st
import duckdb
import pandas as pd
import time
import requests
from src.app.config import settings
from src.rag.pipeline import answer as local_answer
from src.bi.load_data import load_all


st.set_page_config(page_title="RAG + BI POC", layout="wide")

@st.cache_data
def get_data():
    return load_all()

sales, support = get_data()

# --------- Layout ----------
st.title("POC: RAG + Business Intelligence (100% local y gratuito)")

tabs = st.tabs(["Ventas", "Soporte", "RAG", "Agente"])

# ---- Ventas ----
with tabs[0]:
    st.header("Indicadores de Ventas")
    con = duckdb.connect(database=":memory:")
    con.register("sales", sales)

    kpis = con.execute("""
        SELECT
          SUM(sales) AS total_sales,
          SUM(cost)  AS total_cost,
          SUM(sales - cost) AS total_profit
        FROM sales
    """).fetchdf()

    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas totales", f"{int(kpis['total_sales'][0]):,}".replace(",", "."))
    col2.metric("Coste total", f"{int(kpis['total_cost'][0]):,}".replace(",", "."))
    col3.metric("Beneficio total", f"{int(kpis['total_profit'][0]):,}".replace(",", "."))

    mtrend = con.execute("""
        SELECT date_trunc('month', date) AS month,
               SUM(sales) AS sales_m
        FROM sales
        GROUP BY 1 ORDER BY 1
    """).fetchdf()

    st.subheader("Serie temporal de ventas")
    st.line_chart(mtrend.set_index("month"))

    st.subheader("Ventas por región y producto")
    by_cat = con.execute("""
        SELECT region, product, SUM(sales) AS s
        FROM sales
        GROUP BY 1,2
        ORDER BY 1,2
    """).fetchdf()
    st.dataframe(by_cat, use_container_width=True)

# ---- Soporte ----
with tabs[1]:
    st.header("Indicadores de Soporte")
    con = duckdb.connect(database=":memory:")
    con.register("support", support)

    agg = con.execute("""
        SELECT
          COUNT(*) AS tickets,
          AVG(resolution_hours) AS avg_hours
        FROM support
    """).fetchdf()

    c1, c2 = st.columns(2)
    c1.metric("Tickets", int(agg["tickets"][0]))
    c2.metric("Resolución media (h)", f"{agg['avg_hours'][0]:.1f}")

    st.subheader("Tickets por prioridad")
    pr = con.execute("""
        SELECT priority, COUNT(*) AS n
        FROM support GROUP BY 1 ORDER BY 1
    """).fetchdf()
    st.bar_chart(pr.set_index("priority"))

    st.subheader("Distribución de tiempos de resolución")
    st.line_chart(support[["resolved_at", "resolution_hours"]].set_index("resolved_at").rolling(7).mean().dropna())

# ---- RAG ----
with tabs[2]:
    st.header("Consulta a RAG")
    mode = st.radio("Ejecución", ["API FastAPI", "Llamada local"], horizontal=True)
    q = st.text_input("Pregunta", "¿Qué contiene el documento de ejemplo?")
    top_k = st.slider("Pasajes a recuperar (top_k)", 1, 10, 5)

    if st.button("Preguntar"):
        t0 = time.time()
        if mode == "API FastAPI":
            try:
                r = requests.post("http://127.0.0.1:8000/ask", json={"query": q, "top_k": top_k}, timeout=20)
                r.raise_for_status()
                out = r.json()
            except Exception as e:
                st.error(f"No se pudo contactar con la API: {e}")
                st.stop()
        else:
            out = local_answer(q, top_k=top_k)
        t1 = time.time()

        st.subheader("Respuesta")
        st.write(out["answer"])
        st.caption(f"Modo: {out['mode']} | Tiempo: {(t1 - t0)*1000:.0f} ms")

        st.subheader("Pasajes recuperados")
        st.json(out["citations"])

# ---- Agente (BI + RAG) ----
with tabs[3]:
    st.header("Agente BI + RAG")
    q = st.text_input(
        "Pregunta",
        "Ventas del último mes y, según los documentos, ¿qué política de devoluciones aplica?",
        key="agent_q",
    )
    top_k = st.slider("Pasajes RAG (top_k)", 1, 10, 5, key="agent_topk")

    if st.button("Preguntar (Agente)", key="agent_btn"):
        t0 = time.time()
        try:
            r = requests.post(
                "http://127.0.0.1:8000/agent_ask",
                json={"query": q, "top_k": top_k},
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            st.error(f"No se pudo contactar con la API del agente: {e}")
            st.stop()
        t1 = time.time()

        st.subheader("Respuesta combinada")
        st.write(data.get("answer", ""))
        st.caption(f"Modo: {data.get('mode','?')} | Tiempo: {(t1 - t0)*1000:.0f} ms")

        # Tabla BI si existe
        bi = data.get("bi")
        if bi and bi.get("result"):
            st.subheader("Resultado BI (tabla)")
            st.dataframe(pd.DataFrame(bi["result"]), use_container_width=True)
            if bi.get("sql"):
                st.code(bi["sql"], language="sql")

        # Citas RAG si existen
        rag = data.get("rag")
        if rag and rag.get("citations"):
            st.subheader("Citas RAG")
            st.json(rag["citations"])

