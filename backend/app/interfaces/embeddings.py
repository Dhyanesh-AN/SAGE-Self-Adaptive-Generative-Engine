# backend/app/interfaces/embeddings.py
from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    """
    Abstract Base Class defining the contract for any Embedding Provider.
    """
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Convert a single string into a vector (list of floats)."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Convert a list of strings into a list of vectors."""
        pass