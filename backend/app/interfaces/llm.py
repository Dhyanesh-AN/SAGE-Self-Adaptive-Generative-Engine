# backend/app/interfaces/llm.py
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """
    Abstract Base Class for Large Language Models.
    """
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Takes a prompt string and returns the LLM's response."""
        pass