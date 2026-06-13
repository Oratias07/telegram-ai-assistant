import pytest
from app.bot.formatting import escape_markdown_v2, split_message


def test_escape_markdown_v2_special_chars():
    """Test escaping special MarkdownV2 characters."""
    text = "Test_text*with[special]characters"
    result = escape_markdown_v2(text)
    assert "_" in result and "\\_" in result
    assert "*" in result and "\\*" in result


def test_escape_markdown_v2_empty():
    """Test escaping empty string."""
    result = escape_markdown_v2("")
    assert result == ""


def test_escape_markdown_v2_no_special():
    """Test escaping text with no special characters."""
    text = "Simple text"
    result = escape_markdown_v2(text)
    assert result == "Simple text"


def test_split_message_short():
    """Test that short message is not split."""
    text = "Short message"
    result = split_message(text, max_length=100)
    assert result == ["Short message"]


def test_split_message_exact_length():
    """Test message exactly at max_length."""
    text = "a" * 100
    result = split_message(text, max_length=100)
    assert len(result) == 1
    assert result[0] == text


def test_split_message_over_length():
    """Test message exceeding max_length is split."""
    text = "line1\nline2\nline3\n" * 10
    result = split_message(text, max_length=50)
    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 50


def test_split_message_long_line():
    """Test handling of line longer than max_length."""
    text = "a" * 200 + "\n" + "b" * 50
    result = split_message(text, max_length=100)
    assert len(result) >= 2
