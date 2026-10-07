# scripts/test_ingestion.py
import sys
import os

# Add the backend folder to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ingestion.pipeline import IngestionPipeline

pipeline = IngestionPipeline()

chunks = pipeline.ingest("uploads/SDE3.0.pdf")

print(f"Total chunks: {len(chunks)}")

print(f"\nFirst chunk preview:\n{chunks[0][:200].encode('ascii', errors='replace').decode('ascii')}...")