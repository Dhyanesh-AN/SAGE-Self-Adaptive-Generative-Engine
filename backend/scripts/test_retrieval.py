# scripts/test_retrieval.py
import sys
import os

# Add the backend folder to the Python path so we can import our app modules
# Since this script lives in backend/scripts/, we go up one level to reach backend/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.integrations.embeddings.bge import BGEEmbeddingProvider
from app.integrations.vector_db.qdrant import QdrantProvider

def run_test():
    print("[*] Initializing Test...")
    
    # 1. Load our providers
    embedding_provider = BGEEmbeddingProvider()
    vector_db = QdrantProvider()

    # 2. Define a test query
    # Change this to something you know is inside the PDF you uploaded!
    test_query = "What is this document about?" 
    
    print(f"\n[?] Searching for: '{test_query}'")

    # 3. Embed the query (turn the question into a vector)
    query_vector = embedding_provider.embed_text(test_query)

    # 4. Search Qdrant
    results = vector_db.search(query_vector=query_vector, limit=3)

    # 5. Display the results
    print(f"\n[+] Found {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        score = result.get("similarity_score", 0)
        source = result.get("source_document", "Unknown")
        text = result.get("text", "")
        
        print(f"--- Result {i} (Score: {score:.4f}) ---")
        print(f"  Source: {source}")
        # Print first 200 characters of the chunk so it doesn't flood the terminal
        print(f"  Text: {text[:200]}...\n")

if __name__ == "__main__":
    run_test()