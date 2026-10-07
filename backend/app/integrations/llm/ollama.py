# backend/app/integrations/llm/ollama.py
from langchain_community.llms import Ollama
from app.interfaces.llm import LLMProvider
from app.core.logger import logger

class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str = "llama3.2"):
        logger.info(f"Connecting to local Ollama model: {model_name}")
        self.llm = Ollama(model=model_name)

    def generate(self, prompt: str) -> str:
        # invoke() sends the prompt to the running Ollama instance
        response = self.llm.invoke(prompt)
        return response