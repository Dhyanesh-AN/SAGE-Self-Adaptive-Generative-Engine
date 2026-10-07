# backend/app/api/routes/query.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse 
from pydantic import BaseModel

from app.agent.workflow import AgentWorkflow

router = APIRouter(prefix="/query", tags=["Query"])

# 1. Lazy load the agent workflow
_agent = None

def get_agent() -> AgentWorkflow:
    global _agent
    if _agent is None:
        _agent = AgentWorkflow()
    return _agent

class QueryRequest(BaseModel):
    question: str

@router.post("/")
async def ask_question(
    request: QueryRequest, 
    agent: AgentWorkflow = Depends(get_agent)
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    try:
        result = agent.run(request.question)
        return {
            "answer": result["answer"],
            "sources": result["context"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream")
async def stream_question(
    question: str, 
    agent: AgentWorkflow = Depends(get_agent)
):
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    return StreamingResponse(
        agent.stream_events(question), 
        media_type="text/event-stream"
    )