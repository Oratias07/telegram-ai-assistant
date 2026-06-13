import pytest
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock
from app.store.db import init_db
from app.store.conversations import ConversationStore
from app.services.chat import ChatService, SYSTEM_PROMPT


@pytest.fixture
def temp_db():
    db_path = tempfile.mktemp(suffix=".db")
    init_db(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def chat_service(temp_db):
    store = ConversationStore(temp_db)
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value="LLM response")
    service = ChatService(llm=mock_llm, store=store, max_turns=12)
    return service, mock_llm, store


@pytest.mark.asyncio
async def test_reply_persists_user_message(chat_service):
    service, _, store = chat_service

    reply = await service.reply("chat_1", "Hello")

    history = store.history("chat_1")
    assert len(history) == 2  # user + assistant
    assert history[0].role == "user"
    assert history[0].content == "Hello"


@pytest.mark.asyncio
async def test_reply_persists_assistant_message(chat_service):
    service, mock_llm, store = chat_service
    mock_llm.complete = AsyncMock(return_value="AI response")

    reply = await service.reply("chat_1", "Hello")

    history = store.history("chat_1")
    assert len(history) == 2
    assert history[1].role == "assistant"
    assert history[1].content == "AI response"


@pytest.mark.asyncio
async def test_reply_returns_llm_response(chat_service):
    service, mock_llm, _ = chat_service
    mock_llm.complete = AsyncMock(return_value="Expected response")

    reply = await service.reply("chat_1", "Hello")

    assert reply == "Expected response"


@pytest.mark.asyncio
async def test_reply_includes_system_prompt(chat_service):
    service, mock_llm, store = chat_service

    await service.reply("chat_1", "Hello")

    # Check that LLM was called with system prompt
    call_args = mock_llm.complete.call_args
    messages = call_args[0][0]
    assert messages[0]["role"] == "system"
    assert SYSTEM_PROMPT in messages[0]["content"]


@pytest.mark.asyncio
async def test_reply_builds_history(chat_service):
    service, mock_llm, store = chat_service

    await service.reply("chat_1", "First")
    await service.reply("chat_1", "Second")

    call_args = mock_llm.complete.call_args
    messages = call_args[0][0]

    user_messages = [m for m in messages if m["role"] == "user"]
    assert len(user_messages) == 2
    assert user_messages[0]["content"] == "First"
    assert user_messages[1]["content"] == "Second"


@pytest.mark.asyncio
async def test_reply_chat_id_isolation(chat_service):
    service, mock_llm, store = chat_service

    await service.reply("chat_1", "Message for chat 1")
    await service.reply("chat_2", "Message for chat 2")

    history_1 = store.history("chat_1")
    history_2 = store.history("chat_2")

    assert len(history_1) == 2
    assert len(history_2) == 2
    assert history_1[0].content == "Message for chat 1"
    assert history_2[0].content == "Message for chat 2"
