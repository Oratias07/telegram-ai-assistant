import pytest
from unittest.mock import patch, MagicMock
from app.services.search import shallow, Result


@pytest.mark.asyncio
async def test_shallow_returns_results():
    """Test that shallow search returns parsed results."""
    with patch("app.services.search.DDGS") as mock_ddgs_class:
        mock_ddgs = MagicMock()
        mock_ddgs_class.return_value = mock_ddgs
        mock_ddgs.text.return_value = [
            {"title": "Result 1", "href": "http://example.com", "body": "Snippet 1"},
            {"title": "Result 2", "href": "http://example2.com", "body": "Snippet 2"},
        ]

        results = await shallow("test query", k=5)

        assert len(results) == 2
        assert results[0].title == "Result 1"
        assert results[0].url == "http://example.com"
        assert results[1].title == "Result 2"


@pytest.mark.asyncio
async def test_shallow_handles_empty_results():
    """Test that shallow search handles no results gracefully."""
    with patch("app.services.search.DDGS") as mock_ddgs_class:
        mock_ddgs = MagicMock()
        mock_ddgs_class.return_value = mock_ddgs
        mock_ddgs.text.return_value = []

        results = await shallow("nonexistent query", k=5)

        assert results == []


@pytest.mark.asyncio
async def test_shallow_handles_error():
    """Test that shallow search handles errors gracefully."""
    with patch("app.services.search.DDGS") as mock_ddgs_class:
        mock_ddgs = MagicMock()
        mock_ddgs_class.return_value = mock_ddgs
        mock_ddgs.text.side_effect = Exception("Network error")

        results = await shallow("test query", k=5)

        assert results == []


@pytest.mark.asyncio
async def test_shallow_respects_k_parameter():
    """Test that shallow search limits results to k."""
    with patch("app.services.search.DDGS") as mock_ddgs_class:
        mock_ddgs = MagicMock()
        mock_ddgs_class.return_value = mock_ddgs
        mock_ddgs.text.return_value = [
            {"title": f"Result {i}", "href": f"http://example{i}.com", "body": f"Snippet {i}"}
            for i in range(10)
        ]

        results = await shallow("test query", k=3)

        mock_ddgs.text.assert_called_once_with("test query", max_results=3)
