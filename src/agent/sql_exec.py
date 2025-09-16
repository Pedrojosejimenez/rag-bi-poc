import duckdb, pandas as pd
from src.bi.load_data import load_all

def run(intent: str):
    sales, support = load_all()
    con = duckdb.connect(database=":memory:")
    con.register("sales", sales)
    con.register("support", support)
    if intent == "sales_total":
        df = con.execute("SELECT SUM(sales) AS total_sales, SUM(sales-cost) AS profit FROM sales").fetchdf()
        sql = "SELECT SUM(sales) AS total_sales, SUM(sales-cost) AS profit FROM sales"
    elif intent == "sales_by_region":
        df = con.execute("SELECT region, SUM(sales) s FROM sales GROUP BY 1 ORDER BY s DESC").fetchdf()
        sql = "SELECT region, SUM(sales) s FROM sales GROUP BY 1 ORDER BY s DESC"
    elif intent == "sales_by_product":
        df = con.execute("SELECT product, SUM(sales) s FROM sales GROUP BY 1 ORDER BY s DESC").fetchdf()
        sql = "SELECT product, SUM(sales) s FROM sales GROUP BY 1 ORDER BY s DESC"
    elif intent == "sales_trend_m":
        df = con.execute("SELECT date_trunc('month',date) m, SUM(sales) s FROM sales GROUP BY 1 ORDER BY 1").fetchdf()
        sql = "SELECT date_trunc('month',date) m, SUM(sales) s FROM sales GROUP BY 1 ORDER BY 1"
    elif intent == "support_kpis":
        df = con.execute("SELECT COUNT(*) tickets, AVG(resolution_hours) avg_h FROM support").fetchdf()
        sql = "SELECT COUNT(*) tickets, AVG(resolution_hours) avg_h FROM support"
    else:
        df = pd.DataFrame()
        sql = ""
    return {"intent": intent, "sql": sql, "result": df.to_dict(orient="records")}
