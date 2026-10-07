# backend/app/agent/workflow.py
from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
# IMPORT THE NEW REFLECT NODE
from app.agent.nodes import retrieve_node, answer_node, review_node, reflect_node 
from app.core.logger import logger
import json

def check_relevance(state: AgentState) -> str:
    """Router: Decides if we answer, reflect, or give up."""
    if state.get("is_relevant"):
        return "answerer"
    
    # If not relevant, check if we have retried too many times
    if state.get("retry_count", 0) < 3:
        logger.info("[Router] Context irrelevant. Triggering Reflection...")
        return "reflector"
    else:
        logger.info("[Router] Max retries reached. Stopping execution.")
        return END

class AgentWorkflow:
    def __init__(self):
        workflow = StateGraph(AgentState)

        # 1. Add all 4 Nodes
        workflow.add_node("retriever", retrieve_node)
        workflow.add_node("reviewer", review_node)
        workflow.add_node("reflector", reflect_node) # <-- New
        workflow.add_node("answerer", answer_node)

        # 2. Define the Graph Edges (The Loop)
        workflow.add_edge(START, "retriever")
        workflow.add_edge("retriever", "reviewer")
        
        # The Conditional Router
        workflow.add_conditional_edges(
            "reviewer", 
            check_relevance, 
            {
                "answerer": "answerer",
                "reflector": "reflector", # If bad, go to reflector
                END: END
            }
        )
        
        # Once we reflect and get a new query, loop BACK to the retriever!
        workflow.add_edge("reflector", "retriever") 
        
        workflow.add_edge("answerer", END)

        self.app = workflow.compile()
        logger.info("Agent Workflow compiled successfully.")

    def run(self, question: str):
        initial_state = {
            "original_question": question,
            "search_query": question,
            "context": [],
            "answer": "",
            "is_relevant": False,
            "retry_count": 0
        }
        
        final_state = self.app.invoke(initial_state)
        
        if not final_state.get("is_relevant"):
            final_state["answer"] = "I searched the knowledge base multiple times but couldn't find relevant information to answer your question."

        return final_state

    def stream_events(self, question: str):
        """Yields Server-Sent Events (SSE) as the graph processes the query."""
        initial_state = {
            "original_question": question,
            "search_query": question,
            "context": [],
            "answer": "",
            "is_relevant": False,
            "retry_count": 0
        }
        
        # self.app.stream() yields data every time a node finishes running!
        for output in self.app.stream(initial_state):
            # 'output' is a dictionary where the key is the node name (e.g., 'retriever')
            for node_name, state_update in output.items():
                
                # Build an event message
                event_data = {
                    "node": node_name,
                    "status": f"Running {node_name}..."
                }
                
                # Add some custom details based on which node just ran
                if node_name == "reviewer":
                    if state_update.get("is_relevant"):
                        event_data["status"] = "✅ Documents are relevant. Generating answer..."
                    else:
                        event_data["status"] = "❌ Documents irrelevant. Deciding next steps..."
                        
                elif node_name == "reflector":
                    event_data["status"] = f"🔄 Rewrote query to: '{state_update.get('search_query')}'"
                    
                elif node_name == "answerer":
                    event_data["status"] = "✨ Answer generated."
                    event_data["answer"] = state_update.get("answer")

                # SSE format requires "data: <json string>\n\n"
                yield f"data: {json.dumps(event_data)}\n\n"
                
        # If the graph ended without answering (e.g. hit the retry limit)
        final_state = output.get(node_name, {})
        if not final_state.get("is_relevant") and node_name != "answerer":
            fallback = {
                "node": "end",
                "status": "🛑 Reached maximum retries. Could not find answer.",
                "answer": "I searched the knowledge base multiple times but couldn't find relevant information."
            }
            yield f"data: {json.dumps(fallback)}\n\n"