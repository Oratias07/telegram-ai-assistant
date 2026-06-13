import ipaddress
import socket
from urllib.parse import urlparse


def is_safe_url(url: str) -> bool:
    """Check if URL is safe to fetch (no SSRF attack vectors).

    Blocks private/loopback/link-local/reserved IPs and non-http(s) schemes.

    Args:
        url: URL to check

    Returns:
        True if URL is safe to fetch, False otherwise
    """
    if not url.startswith(("http://", "https://")):
        return False

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False

        ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        return not (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        )
    except (socket.gaierror, ValueError, OSError):
        return False


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input: remove null bytes, truncate.

    Args:
        text: input text
        max_length: maximum length

    Returns:
        sanitized text
    """
    text = text.replace("\x00", "")
    return text[:max_length]
