from abc import ABC, abstractmethod
import logging
from urllib.parse import quote
import httpx

logger = logging.getLogger(__name__)


class ImageGenerator(ABC):
    """Interface for image generation providers."""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate image from prompt.

        Args:
            prompt: text prompt for image generation

        Returns:
            URL to generated image, or empty string on failure
        """
        pass


class PollinationsGenerator(ImageGenerator):
    """Pollinations.ai image generation client."""

    def __init__(self, timeout: int = 45):
        self.timeout = timeout
        self.base_url = "https://image.pollinations.ai"

    async def generate(self, prompt: str) -> str:
        """Generate image using Pollinations API."""
        url = f"{self.base_url}/prompt/{quote(prompt)}"
        logger.info(f"Pollinations request: {url}")
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    logger.info(f"Pollinations success: {response.url}")
                    return str(response.url)
                logger.error(
                    f"Pollinations HTTP {response.status_code} for prompt={prompt!r} "
                    f"body={response.text[:500]!r}"
                )
                return ""
        except httpx.TimeoutException as e:
            logger.error(f"Pollinations timeout after {self.timeout}s for prompt={prompt!r}: {e}", exc_info=True)
            return ""
        except Exception as e:
            logger.error(f"Pollinations unexpected error for prompt={prompt!r}: {e}", exc_info=True)
            return ""
