import pytest
from unittest.mock import patch, MagicMock
from app.services.llm import GroqClient, LLMClient


def test_llm_client_is_abstract():
    """Test that LLMClient cannot be instantiated."""
    with pytest.raises(TypeError):
        LLMClient()


@pytest.mark.asyncio
async def test_groq_client_complete():
    """Test Groq client sends messages and returns response."""
    with patch("app.services.llm.Groq") as mock_groq_class:
        mock_groq_instance = MagicMock()
        mock_groq_class.return_value = mock_groq_instance

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_groq_instance.chat.completions.create.return_value = mock_response

        client = GroqClient(api_key="test_key")
        messages = [{"role": "user", "content": "Hello"}]

        result = await client.complete(messages)

        assert result == "Test response"
        mock_groq_instance.chat.completions.create.assert_called_once()
        call_kwargs = mock_groq_instance.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "llama-3.3-70b-versatile"
        assert call_kwargs["messages"] == messages


def test_groq_client_is_llm_client():
    """Test that GroqClient implements LLMClient interface."""
    assert issubclass(GroqClient, LLMClient)
