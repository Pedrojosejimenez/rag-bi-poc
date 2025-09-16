from dataclasses import dataclass

BI_KWS = {"venta","ventas","facturación","beneficio","coste","región","producto",
          "tendencia","mes","trimestral","tickets","prioridad","resolución","sla","ttr"}
RAG_KWS = {"documento","pdf","cita","citas","fuente","según","sección","manual","política","normativa"}

@dataclass
class Route:
    action: str         # 'bi' | 'rag' | 'both'
    bi_intent: str|None # p.ej. 'sales_total'

def classify(q: str) -> Route:
    ql = q.lower()
    has_bi  = any(k in ql for k in BI_KWS)
    has_rag = any(k in ql for k in RAG_KWS)
    if has_bi and has_rag:
        return Route("both","sales_total")
    if has_bi:
        # heurística simple de intent
        if "región" in ql: return Route("bi","sales_by_region")
        if "producto" in ql: return Route("bi","sales_by_product")
        if "tickets" in ql or "resolución" in ql: return Route("bi","support_kpis")
        if "tendencia" in ql or "mes" in ql: return Route("bi","sales_trend_m")
        return Route("bi","sales_total")
    return Route("rag", None)
