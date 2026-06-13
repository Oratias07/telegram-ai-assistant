from abc import ABC, abstractmethod
import logging
import random
from urllib.parse import quote
import httpx

logger = logging.getLogger(__name__)


class ImageGenerator(ABC):
    """Interface for image generation providers."""

    @abstractmethod
    async def generate(self, prompt: str) -> bytes | str:
        """Generate image from prompt.

        Returns:
            Raw image bytes, a URL string, or empty string on failure.
        """
        pass


class HuggingFaceGenerator(ImageGenerator):
    """Hugging Face Inference API — returns raw image bytes."""

    ENDPOINT = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

    def __init__(self, token: str, timeout: int = 60):
        self.token = token
        self.timeout = timeout

    async def generate(self, prompt: str) -> bytes:
        logger.info(f"HuggingFace request: model=FLUX.1-schnell prompt={prompt!r}")
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.ENDPOINT,
                    headers=headers,
                    json={"inputs": prompt},
                )
                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "")
                    if "image" in content_type:
                        logger.info(f"HuggingFace success: {len(response.content)} bytes, content-type={content_type}")
                        return response.content
                    logger.error(
                        f"HuggingFace 200 but unexpected content-type={content_type!r} "
                        f"body={response.text[:200]!r}"
                    )
                    return b""
                logger.error(
                    f"HuggingFace HTTP {response.status_code} for prompt={prompt!r} "
                    f"body={response.text[:500]!r}"
                )
                return b""
        except httpx.TimeoutException as e:
            logger.error(f"HuggingFace timeout after {self.timeout}s for prompt={prompt!r}: {e}", exc_info=True)
            return b""
        except Exception as e:
            logger.error(f"HuggingFace unexpected error for prompt={prompt!r}: {e}", exc_info=True)
            return b""


class PollinationsGenerator(ImageGenerator):
    """Pollinations.ai image generation — returns a URL."""

    def __init__(self, timeout: int = 45):
        self.timeout = timeout
        self.base_url = "https://image.pollinations.ai"

    async def generate(self, prompt: str) -> str:
        seed = random.randint(1, 2**31)
        url = (
            f"{self.base_url}/prompt/{quote(prompt)}"
            f"?nologo=true&private=true&model=flux&width=512&height=512&seed={seed}"
        )
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


class FallbackImageGenerator(ImageGenerator):
    """Tries primary generator, falls back to secondary on failure."""

    def __init__(self, primary: ImageGenerator, fallback: ImageGenerator):
        self.primary = primary
        self.fallback = fallback

    async def generate(self, prompt: str) -> bytes | str:
        result = await self.primary.generate(prompt)
        if result:
            return result
        logger.warning("Primary image generator failed, trying fallback")
        return await self.fallback.generate(prompt)
