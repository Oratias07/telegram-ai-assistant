from abc import ABC, abstractmethod
import httpx


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

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.base_url = "https://image.pollinations.ai"

    async def generate(self, prompt: str) -> str:
        """Generate image using Pollinations API."""
        try:
            url = f"{self.base_url}/prompt/{prompt}"
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, limits=httpx.Limits(max_redirect_loops=3))
                if response.status_code == 200:
                    return str(response.url)
                return ""
        except Exception:
            return ""
