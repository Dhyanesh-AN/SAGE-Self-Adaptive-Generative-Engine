# backend/app/integrations/embeddings/bge.py
from typing import List
from sentence_transformers import SentenceTransformer
from app.interfaces.embeddings import EmbeddingProvider
from app.core.logger import logger

class BGEEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        logger.info(f"Loading embedding model: {model_name}")
        # Initialize the model. It will download the weights on the first run.
        self.model = SentenceTransformer(model_name)
        
    def embed_text(self, text: str) -> List[float]:
        """
        Generates an embedding for a single text.
        BGE recommends adding 'Represent this sentence for searching relevant passages: ' 
        for queries, but for documents we just embed the raw text.
        """
        # encode() returns a numpy array, we convert it to a standard Python list
        vector = self.model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for multiple chunks efficiently.
        """
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()