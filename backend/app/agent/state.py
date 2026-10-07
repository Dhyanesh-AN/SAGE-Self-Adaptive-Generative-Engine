# backend/app/agent/state.py
from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    """
    This represents the memory of our AI Agent.
    As the graph runs, nodes will update these variables.
    """
    original_question: str
    search_query: str      # The actual query sent to Qdrant (Planner might alter this later)
    context: List[Dict[str, Any]] # Retrieved chunks
    answer: str            # The final generated answer
    is_relevant: bool
    retry_count: int