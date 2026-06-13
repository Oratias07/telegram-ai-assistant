import httpx
import trafilatura
from app.core.security import is_safe_url


async def fetch_and_extract(url: str, timeout: int = 10, max_size: int = 5_000_000) -> str:
    """Fetch URL and extract main content with trafilatura.

    Args:
        url: URL to fetch
        timeout: request timeout in seconds
        max_size: max response size in bytes

    Returns:
        extracted text, or empty string on failure
    """
    if not is_safe_url(url):
        return ""

    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, limits=httpx.Limits(max_redirect_loops=5))
            if response.status_code != 200 or len(response.content) > max_size:
                return ""

            content = trafilatura.extract(response.text)
            return content or ""
    except Exception:
        return ""
