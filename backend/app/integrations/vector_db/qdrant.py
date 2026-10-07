# backend/app/integrations/vector_db/qdrant.py
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.interfaces.vector_db import VectorDBProvider
from app.core.config import settings
from app.core.logger import logger

class QdrantProvider(VectorDBProvider):
    def __init__(self):
        logger.info(f"Connecting to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        # Added a 60-second timeout to accommodate larger file processing
        self.client = QdrantClient(
            host=settings.QDRANT_HOST, 
            port=settings.QDRANT_PORT,
            timeout=60.0 
        )
        self.collection_name = settings.COLLECTION_NAME
        self.create_collection()

    def create_collection(self) -> None:
        """Checks if the collection exists, creates it if it doesn't."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            logger.info(f"Creating collection '{self.collection_name}' in Qdrant...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=settings.EMBEDDING_DIMENSIONS,
                    distance=models.Distance.COSINE
                ),
            )
        else:
            logger.info(f"Collection '{self.collection_name}' already exists.")

    def upsert(self, ids: List[str], vectors: List[List[float]], payloads: List[Dict[str, Any]]) -> None:
        """Inserts document chunks into Qdrant in batches to prevent timeouts."""
        
        points = [
            models.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
            for point_id, vector, payload in zip(ids, vectors, payloads)
        ]
        
        # --- NEW BATCHING LOGIC ---
        batch_size = 100
        total_points = len(points)
        
        logger.info(f"Starting upload of {total_points} chunks in batches of {batch_size}...")
        
        for i in range(0, total_points, batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            logger.info(f"Upserted batch {i // batch_size + 1}/{(total_points + batch_size - 1) // batch_size}")

        logger.info(f"Successfully finished upserting {total_points} chunks into Qdrant.")

    def search(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Searches Qdrant and returns the metadata (payload) of the best matches."""
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True
        )
        
        results = []
        for hit in search_results.points:
            result_data = hit.payload or {}
            result_data["similarity_score"] = hit.score
            results.append(result_data)
            
        return results