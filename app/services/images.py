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


class GeminiImagenGenerator(ImageGenerator):
    """Gemini 2.5 Flash image generation via generateContent — returns raw image bytes."""

    ENDPOINT = (
        "https://generativelanguage.googleapis.com/v1beta"
        "/models/gemini-2.5-flash-image:generateContent"
    )
    name = "Gemini 2.5 Flash"

    def __init__(self, api_key: str, timeout: int = 60):
        self.api_key = api_key
        self.timeout = timeout

    async def generate(self, prompt: str) -> bytes:
        import base64
        url = f"{self.ENDPOINT}?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]},
        }
        logger.info(f"Gemini 2.5 Flash image request: model=gemini-2.5-flash-image prompt={prompt!r}")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates") or []
                    if not candidates:
                        logger.error(f"Gemini 2.5 Flash: no candidates in response: {data!r}")
                        return b""
                    parts = (candidates[0].get("content") or {}).get("parts") or []
                    image_part = next((p for p in parts if "inlineData" in p), None)
                    if not image_part:
                        logger.error(f"Gemini 2.5 Flash: no inlineData part in parts: {parts!r}")
                        return b""
                    inline = image_part["inlineData"]
                    image_bytes = base64.b64decode(inline["data"])
                    logger.info(f"Gemini 2.5 Flash success: {len(image_bytes)} bytes mime={inline.get('mimeType')}")
                    return image_bytes
                logger.error(
                    f"Gemini 2.5 Flash HTTP {response.status_code} for prompt={prompt!r} "
                    f"body={response.text[:500]!r}"
                )
                return b""
        except httpx.TimeoutException as e:
            logger.error(f"Gemini 2.5 Flash timeout after {self.timeout}s for prompt={prompt!r}: {e}", exc_info=True)
            return b""
        except Exception as e:
            logger.error(f"Gemini 2.5 Flash unexpected error for prompt={prompt!r}: {e}", exc_info=True)
            return b""


class PollinationsGenerator(ImageGenerator):
    """Pollinations.ai image generation — returns a URL."""

    name = "Pollinations.ai"

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
        self.name = f"{primary.name} / {fallback.name}"

    async def generate(self, prompt: str) -> bytes | str:
        result = await self.primary.generate(prompt)
        if result:
            return result
        logger.warning("Primary image generator failed, trying fallback")
        return await self.fallback.generate(prompt)
