from src.agent.router import classify
from src.agent import sql_exec
from src.rag.pipeline import answer as rag_answer

def agent_answer(query: str, top_k: int = 5):
    route = classify(query)
    bi_out, rag_out = None, None
    if route.action in ("bi","both"):
        bi_out = sql_exec.run(route.bi_intent)
    if route.action in ("rag","both"):
        rag_out = rag_answer(query, top_k=top_k)
    # Composición final
    parts = []
    mode = route.action
    if bi_out and bi_out["result"]:
        parts.append(f"[BI/{bi_out['intent']}] SQL: {bi_out['sql']}")
    if rag_out:
        parts.append(f"[RAG/{rag_out['mode']}] {rag_out['answer']}")
    return {"mode": mode, "bi": bi_out, "rag": rag_out, "answer": "\n\n".join(parts)}
