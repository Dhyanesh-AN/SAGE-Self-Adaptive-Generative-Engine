# backend/app/retrieval/hybrid.py
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import nltk

# Download the punkt tokenizer for word splitting
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt_tab')
    nltk.download('punkt')

class HybridRetriever:
    def __init__(self):
        self.corpus_chunks: List[Dict[str, Any]] = []
        self.bm25 = None
        
    def update_index(self, payloads: List[Dict[str, Any]]):
        """Builds the BM25 index from all documents in our knowledge base."""
        self.corpus_chunks = payloads
        
        # Tokenize the text (split paragraphs into lists of lowercase words)
        tokenized_corpus = [
            nltk.word_tokenize(payload.get("text", "").lower()) 
            for payload in self.corpus_chunks
        ]
        
        # Initialize the BM25 engine
        if tokenized_corpus:
            self.bm25 = BM25Okapi(tokenized_corpus)

    def bm25_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Performs a keyword search."""
        if not self.bm25:
            return []
            
        tokenized_query = nltk.word_tokenize(query.lower())
        
        # Get BM25 scores for all chunks
        scores = self.bm25.get_scores(tokenized_query)
        
        # Pair chunks with their scores and sort them descending
        scored_chunks = list(zip(self.corpus_chunks, scores))
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # Return the top 'limit' chunks
        return [chunk for chunk, score in scored_chunks[:limit] if score > 0]

    def reciprocal_rank_fusion(self, dense_results: List[Dict[str, Any]], sparse_results: List[Dict[str, Any]], k: int = 60) -> List[Dict[str, Any]]:
        """
        Combines Dense (Qdrant) and Sparse (BM25) results using RRF.
        Formula: RRF_Score = 1 / (k + rank)
        """
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}

        # Process Dense Results
        for rank, result in enumerate(dense_results):
            text = result.get("text", "")
            if text not in chunk_map:
                chunk_map[text] = result
            rrf_scores[text] = rrf_scores.get(text, 0.0) + (1.0 / (k + rank + 1))

        # Process Sparse (BM25) Results
        for rank, result in enumerate(sparse_results):
            text = result.get("text", "")
            if text not in chunk_map:
                chunk_map[text] = result
            rrf_scores[text] = rrf_scores.get(text, 0.0) + (1.0 / (k + rank + 1))

        # Sort combined results by RRF score
        sorted_texts = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        
        # Format the final list
        final_results = []
        for text in sorted_texts:
            chunk = chunk_map[text]
            chunk["rrf_score"] = rrf_scores[text]
            final_results.append(chunk)

        return final_results