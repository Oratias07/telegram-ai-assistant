import pytest
from app.core.security import is_safe_url, sanitize_input


def test_is_safe_url_valid_http():
    """Test that valid http URL passes."""
    assert is_safe_url("http://example.com/page") is True


def test_is_safe_url_valid_https():
    """Test that valid https URL passes."""
    assert is_safe_url("https://google.com") is True


def test_is_safe_url_no_scheme():
    """Test that URL without scheme is rejected."""
    assert is_safe_url("example.com") is False


def test_is_safe_url_ftp():
    """Test that non-http scheme is rejected."""
    assert is_safe_url("ftp://example.com") is False


def test_is_safe_url_localhost():
    """Test that localhost is blocked."""
    assert is_safe_url("http://localhost:8000") is False


def test_is_safe_url_127():
    """Test that 127.0.0.1 is blocked."""
    assert is_safe_url("http://127.0.0.1") is False


def test_is_safe_url_private_10():
    """Test that 10.x private IP is blocked."""
    assert is_safe_url("http://10.0.0.1") is False


def test_is_safe_url_private_192():
    """Test that 192.168.x private IP is blocked."""
    assert is_safe_url("http://192.168.1.1") is False


def test_is_safe_url_metadata():
    """Test that metadata service IP is blocked."""
    assert is_safe_url("http://169.254.169.254") is False


def test_is_safe_url_invalid_hostname():
    """Test that invalid hostname is rejected."""
    assert is_safe_url("http://invalid..example.com") is False


def test_sanitize_input_removes_nulls():
    """Test that null bytes are removed."""
    text = "hello\x00world"
    result = sanitize_input(text)
    assert "\x00" not in result
    assert "helloworld" == result


def test_sanitize_input_truncates():
    """Test that input is truncated."""
    text = "a" * 2000
    result = sanitize_input(text, max_length=100)
    assert len(result) == 100


def test_sanitize_input_normal():
    """Test that normal input passes through."""
    text = "Hello world"
    result = sanitize_input(text)
    assert result == text
