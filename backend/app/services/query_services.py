# backend/app/services/query_services.py
from typing import Dict, Any

from app.integrations.embeddings.bge import BGEEmbeddingProvider
from app.integrations.vector_db.qdrant import QdrantProvider
from app.integrations.llm.ollama import OllamaProvider
from app.retrieval.hybrid import HybridRetriever
from app.core.logger import logger

class QueryService:
    def __init__(self):
        self.embedding_provider = BGEEmbeddingProvider()
        self.vector_db = QdrantProvider()
        self.llm_provider = OllamaProvider()
        self.hybrid_retriever = HybridRetriever()

    def query(self, question: str) -> Dict[str, Any]:
        logger.info(f"Processing query: '{question}'")

        # 1. Fetch ALL metadata from Qdrant to build the BM25 keyword index 
        # (In a massive production app, you'd use a dedicated database for this, but for resumes this is perfect)
        all_chunks = self.vector_db.search(query_vector=self.embedding_provider.embed_text(""), limit=1000)
        self.hybrid_retriever.update_index(all_chunks)

        # 2. Dense Search (Semantic meaning)
        logger.info("Executing Dense Search (Qdrant)...")
        query_vector = self.embedding_provider.embed_text(question)
        dense_results = self.vector_db.search(query_vector=query_vector, limit=5)
        
        # 3. Sparse Search (Exact keywords)
        logger.info("Executing Sparse Search (BM25)...")
        sparse_results = self.hybrid_retriever.bm25_search(query=question, limit=5)

        # 4. Reciprocal Rank Fusion
        logger.info("Applying Reciprocal Rank Fusion (RRF)...")
        combined_results = self.hybrid_retriever.reciprocal_rank_fusion(
            dense_results=dense_results, 
            sparse_results=sparse_results
        )
        
        # Take the absolute best 4 chunks after fusion
        top_results = combined_results[:4]

        if not top_results:
            return {
                "answer": "I couldn't find any relevant information.",
                "sources": []
            }

        # 5. Build the Prompt
        context_text = "\n\n---\n\n".join(
            [f"Source: {res.get('source_document', 'Unknown')}\nText: {res.get('text', '')}" 
             for res in top_results]
        )

        prompt = f"""You are SAGE, a helpful AI assistant. Answer the user's question using ONLY the context provided below. 
If the answer is not contained in the context, say "I don't have enough information to answer that." Do not make up answers.

Context:
{context_text}

Question: {question}

Answer:"""

        # 6. Generate Answer
        logger.info("Generating answer with LLM...")
        answer = self.llm_provider.generate(prompt)

        return {
            "answer": answer,
            "sources": top_results
        }