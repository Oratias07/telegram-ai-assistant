import time
import pytest
from app.core.rate_limit import RateLimiter


def test_rate_limiter_allows_requests():
    """Test that requests within limit are allowed."""
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is True


def test_rate_limiter_blocks_exceeded():
    """Test that requests exceeding limit are blocked."""
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is False


def test_rate_limiter_isolation():
    """Test that different users have separate limits."""
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is False

    assert limiter.is_allowed("user2") is True
    assert limiter.is_allowed("user2") is True
    assert limiter.is_allowed("user2") is False


def test_rate_limiter_window_reset():
    """Test that limit resets after window expires."""
    limiter = RateLimiter(max_requests=1, window_seconds=1)
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is False

    time.sleep(1.1)

    assert limiter.is_allowed("user1") is True


def test_rate_limiter_get_retry_after():
    """Test retry_after calculation."""
    limiter = RateLimiter(max_requests=1, window_seconds=10)
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is False

    retry_after = limiter.get_retry_after("user1")
    assert 0 < retry_after <= 10
