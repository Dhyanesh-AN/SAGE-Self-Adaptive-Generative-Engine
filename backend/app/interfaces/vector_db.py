# backend/app/interfaces/vector_db.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class VectorDBProvider(ABC):
    """
    Abstract Base Class for Vector Database operations.
    """
    
    @abstractmethod
    def create_collection(self) -> None:
        """Creates the collection/index if it doesn't exist."""
        pass

    @abstractmethod
    def upsert(self, ids: List[str], vectors: List[List[float]], payloads: List[Dict[str, Any]]) -> None:
        """
        Inserts or updates vectors and their associated metadata (payload).
        """
        pass

    @abstractmethod
    def search(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Searches for the closest vectors to the query.
        Returns a list of payloads (metadata + text) of the top results.
        """
        pass