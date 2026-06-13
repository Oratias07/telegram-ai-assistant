import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.deep_search import deep_search, _build_synthesis_prompt, Source


@pytest.mark.asyncio
async def test_deep_search_no_results():
    """Test deep search when no shallow results found."""
    mock_llm = AsyncMock()

    with patch("app.services.deep_search.search_service.shallow") as mock_search:
        mock_search.return_value = []

        result = await deep_search("test query", mock_llm)

        assert result.answer == "No relevant sources found."
        assert result.sources == []


@pytest.mark.asyncio
async def test_deep_search_no_extracted_content():
    """Test deep search when all extractions are empty, uses snippets as fallback."""
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value="Synthesized")

    with patch("app.services.deep_search.search_service.shallow") as mock_search:
        mock_search.return_value = [
            MagicMock(url="http://example.com", title="Result 1", snippet="Snippet 1"),
            MagicMock(url="http://example2.com", title="Result 2", snippet="Snippet 2"),
        ]

        with patch("app.services.deep_search.extract.fetch_and_extract") as mock_extract:
            mock_extract.return_value = ""

            result = await deep_search("test query", mock_llm)

            # When extraction fails, fallback to snippets
            assert len(result.sources) == 2
            assert result.sources[0].content == "Snippet 1"


@pytest.mark.asyncio
async def test_deep_search_with_extraction():
    """Test deep search with successful extraction and synthesis."""
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value="Synthesized answer")

    with patch("app.services.deep_search.search_service.shallow") as mock_search:
        mock_search.return_value = [
            MagicMock(url="http://example.com", title="Result 1", snippet="Snippet 1"),
            MagicMock(url="http://example2.com", title="Result 2", snippet="Snippet 2"),
        ]

        with patch("app.services.deep_search.extract.fetch_and_extract") as mock_extract:
            mock_extract.side_effect = ["Content 1", "Content 2"]

            result = await deep_search("test query", mock_llm)

            assert result.answer == "Synthesized answer"
            assert len(result.sources) == 2
            assert result.sources[0].title == "Result 1"
            mock_llm.complete.assert_called_once()


@pytest.mark.asyncio
async def test_deep_search_takes_top_4():
    """Test that deep search only uses top 4 results."""
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value="Answer")

    with patch("app.services.deep_search.search_service.shallow") as mock_search:
        mock_search.return_value = [
            MagicMock(url=f"http://example{i}.com", title=f"Result {i}", snippet=f"Snippet {i}")
            for i in range(10)
        ]

        with patch("app.services.deep_search.extract.fetch_and_extract") as mock_extract:
            mock_extract.side_effect = [f"Content {i}" for i in range(10)]

            result = await deep_search("test query", mock_llm)

            assert len(result.sources) == 4


def test_build_synthesis_prompt():
    """Test synthesis prompt building."""
    sources = [
        Source(url="http://example.com", title="Title 1", content="Content 1"),
        Source(url="http://example2.com", title="Title 2", content="Content 2"),
    ]

    messages = _build_synthesis_prompt("test query", sources)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "research assistant" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert "test query" in messages[1]["content"]
    assert "<source id=1" in messages[1]["content"]
    assert "<source id=2" in messages[1]["content"]
    assert "Content 1" in messages[1]["content"]
    assert "Content 2" in messages[1]["content"]
