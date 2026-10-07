# backend/app/services/upload_service.py
import uuid
import os
from typing import Dict, Any

from app.ingestion.pipeline import IngestionPipeline
from app.integrations.embeddings.bge import BGEEmbeddingProvider
from app.integrations.vector_db.qdrant import QdrantProvider
from app.core.logger import logger

class UploadService:
    def __init__(self):
        self.pipeline = IngestionPipeline()
        # Initialize our new providers!
        self.embedding_provider = BGEEmbeddingProvider()
        self.vector_db = QdrantProvider()

    def upload(self, file_path: str) -> Dict[str, Any]:
        logger.info(f"Starting ingestion for {file_path}")
        
        # 1. Extract and chunk the text (Your existing Sprint 2 code)
        chunks = self.pipeline.ingest(file_path)
        logger.info(f"Generated {len(chunks)} chunks.")

        if not chunks:
            return {"message": "No text extracted from file.", "chunks_processed": 0}

        # 2. Generate Embeddings (Sprint 3)
        logger.info("Generating embeddings for chunks...")
        vectors = self.embedding_provider.embed_batch(chunks)

        # 3. Prepare data for Qdrant (IDs and Metadata)
        file_name = os.path.basename(file_path)
        ids = []
        payloads = []

        for i, chunk_text in enumerate(chunks):
            # Qdrant needs a standard UUID for the ID
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            
            # Metadata is crucial for RAG! We store the actual text here so the LLM can read it later.
            payloads.append({
                "source_document": file_name,
                "chunk_index": i,
                "text": chunk_text
            })

        # 4. Upsert to Qdrant
        logger.info("Saving to Qdrant vector database...")
        self.vector_db.upsert(ids=ids, vectors=vectors, payloads=payloads)

        return {
            "message": "Successfully ingested document into Knowledge Base",
            "file": file_name,
            "chunks_processed": len(chunks),
            "preview": chunks[:2]
        }