import pytest
from unittest.mock import AsyncMock, MagicMock
from app.main import start


@pytest.mark.asyncio
async def test_start_handler():
    """Test that /start handler sends greeting message."""
    mock_reply_text = AsyncMock()
    mock_message = MagicMock()
    mock_message.reply_text = mock_reply_text

    mock_update = MagicMock()
    mock_update.message = mock_message

    mock_context = MagicMock()

    await start(mock_update, mock_context)

    mock_reply_text.assert_called_once()
    call_args = mock_reply_text.call_args
    assert "AI assistant" in call_args[0][0]
