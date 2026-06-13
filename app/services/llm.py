from abc import ABC, abstractmethod
import time
from groq import Groq
from groq import RateLimitError


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

    async def complete(self, messages: list[dict], max_retries: int = 2) -> str:
        """Send messages to Groq and get completion.

        Retries on rate limit (429) with exponential backoff.
        """
        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.7,
                )
                return response.choices[0].message.content
            except RateLimitError:
                if attempt < max_retries:
                    wait = 2 ** attempt
                    time.sleep(wait)
                else:
                    raise
