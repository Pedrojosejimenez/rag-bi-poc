from fastapi import APIRouter
from pydantic import BaseModel
from src.agent.orchestrator import agent_answer

router = APIRouter()

class AgentAsk(BaseModel):
    query: str
    top_k: int = 5

@router.post("/agent_ask")
def agent_ask(req: AgentAsk):
    return agent_answer(req.query, top_k=req.top_k)
