from abc import ABC, abstractmethod
from groq import Groq


class LLMClient(ABC):
    """Interface for LLM providers."""

    @abstractmethod
    async def complete(self, messages: list[dict]) -> str:
        """Send messages and get completion.

        Args:
            messages: list of {role, content} dicts

        Returns:
            LLM response text
        """
        pass


class GroqClient(LLMClient):
    """Groq inference client."""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model

    async def complete(self, messages: list[dict]) -> str:
        """Send messages to Groq and get completion."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content
