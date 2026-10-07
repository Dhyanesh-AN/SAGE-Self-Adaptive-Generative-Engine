# backend/app/agent/nodes.py
from app.agent.state import AgentState
from app.services.query_services import QueryService
from app.core.logger import logger


# We reuse our existing service to do the heavy lifting!
query_service = QueryService()

def retrieve_node(state: AgentState) -> dict:
    """
    Node 1: Retrieves context from the vector database using Hybrid Search.
    """
    query = state.get("search_query", state["original_question"])
    logger.info(f"[Node: Retrieve] Searching for: {query}")
    
    # We will temporarily use the query_service for retrieval logic we already built
    # We need to extract just the retrieval part from your query_service
    
    # Fetch metadata for BM25 (In production, this should be cached)
    all_chunks = query_service.vector_db.search(query_vector=query_service.embedding_provider.embed_text(""), limit=1000)
    query_service.hybrid_retriever.update_index(all_chunks)

    # Dense + Sparse Search
    query_vector = query_service.embedding_provider.embed_text(query)
    dense_results = query_service.vector_db.search(query_vector=query_vector, limit=5)
    sparse_results = query_service.hybrid_retriever.bm25_search(query=query, limit=5)

    # RRF
    combined_results = query_service.hybrid_retriever.reciprocal_rank_fusion(
        dense_results=dense_results, 
        sparse_results=sparse_results
    )
    
    top_results = combined_results[:4]
    
    # Return the updated state
    return {"context": top_results}


def answer_node(state: AgentState) -> dict:
    """
    Node 2: Generates an answer using the LLM and the retrieved context.
    """
    logger.info("[Node: Answer] Generating response...")
    question = state["original_question"]
    context_chunks = state.get("context", [])
    
    if not context_chunks:
        return {"answer": "I couldn't find any relevant information to answer your question."}

    context_text = "\n\n---\n\n".join(
        [f"Source: {res.get('source_document', 'Unknown')}\nText: {res.get('text', '')}" 
         for res in context_chunks]
    )

    prompt = f"""You are SAGE, a helpful AI assistant. Answer the user's question using ONLY the context provided below. 
If the answer is not contained in the context, say "I don't have enough information to answer that." Do not make up answers.

Context:
{context_text}

Question: {question}

Answer:"""

    answer = query_service.llm_provider.generate(prompt)
    
    return {"answer": answer}


def review_node(state: AgentState) -> dict:
    """
    Node 3: Evaluates if the retrieved context actually answers the question.
    Uses a two-stage filter:
      1. Hard threshold on similarity score (fast, no LLM call needed)
      2. LLM grader for borderline cases that pass the threshold
    """
    logger.info("[Node: Reviewer] Evaluating retrieval quality...")
    
    question = state["original_question"]
    context_chunks = state.get("context", [])
    
    if not context_chunks:
        logger.info("❌ No context chunks retrieved.")
        return {"is_relevant": False}

    # --- Stage 1: Similarity Score Pre-Filter ---
    # If the best chunk's score is below this threshold, the retrieval is
    # clearly off-topic. No need to waste an LLM call.
    SIMILARITY_THRESHOLD = 0.65
    best_score = max(chunk.get("similarity_score", 0.0) for chunk in context_chunks)
    logger.info(f"[Reviewer] Best similarity score: {best_score:.4f} (threshold: {SIMILARITY_THRESHOLD})")

    if best_score < SIMILARITY_THRESHOLD:
        logger.info(f"❌ Pre-filter REJECTED: score {best_score:.4f} < {SIMILARITY_THRESHOLD}")
        return {"is_relevant": False}

    # --- Stage 2: LLM Grader for borderline passes ---
    context_text = "\n\n".join([res.get("text", "") for res in context_chunks])

    prompt = f"""You are a strict grader evaluating if retrieved documents are relevant to a user's question.
    
    Question: {question}
    
    Documents:
    {context_text}
    
    Rule 1: If the documents contain the answer to the question, output the exact word "YES".
    Rule 2: If the documents DO NOT contain the answer, output the exact word "NO".
    Rule 3: Output NOTHING ELSE. No explanations. No punctuation.
    
    Result:"""

    response = query_service.llm_provider.generate(prompt).strip().upper()
    logger.info(f"[Reviewer] LLM raw output: '{response}'")
    
    # Must start with YES — handles "YES" and "YES, ..." but not "NO" or garbage
    is_relevant = response.startswith("YES")
    
    if is_relevant:
        logger.info("✅ Documents graded as RELEVANT.")
    else:
        logger.info("❌ Documents graded as IRRELEVANT by LLM.")

    return {"is_relevant": is_relevant}

def reflect_node(state: AgentState) -> dict:
    """
    Node 4: If retrieval fails, rewrite the query to try again.
    """
    logger.info("[Node: Reflector] Rewriting query for better retrieval...")
    
    original_question = state["original_question"]
    current_retries = state.get("retry_count", 0)
    
    prompt = f"""You are an expert search engine query writer. 
    The original user question is: "{original_question}"
    
    Our previous database searches failed to find the answer. 
    Write a completely different, highly optimized search query to find this information in a technical textbook. 
    Output ONLY the new search query. No quotes, no explanations.
    
    New Query:"""
    
    new_query = query_service.llm_provider.generate(prompt).strip()
    logger.info(f"Rewrote query to: '{new_query}'")
    
    # Return the updated search query and increment the retry counter
    return {
        "search_query": new_query,
        "retry_count": current_retries + 1
    }