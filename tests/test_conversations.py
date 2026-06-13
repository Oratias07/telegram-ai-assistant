import pytest
import sqlite3
import tempfile
import time
import os
from app.store.db import init_db
from app.store.conversations import ConversationStore


@pytest.fixture
def temp_db():
    db_path = tempfile.mktemp(suffix=".db")
    init_db(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


def test_append_message(temp_db):
    """Test appending a message to conversation."""
    store = ConversationStore(temp_db)
    store.append("chat_1", "user", "Hello")

    history = store.history("chat_1")
    assert len(history) == 1
    assert history[0].role == "user"
    assert history[0].content == "Hello"


def test_history_window(temp_db):
    """Test that history is limited to max_turns."""
    store = ConversationStore(temp_db)

    for i in range(30):
        store.append("chat_1", "user" if i % 2 == 0 else "assistant", f"Message {i}")

    history = store.history("chat_1", max_turns=6)
    assert len(history) <= 12  # max_turns * 2 in SQL
    assert history[-1].content == "Message 29"


def test_history_chronological(temp_db):
    """Test that history is returned in chronological order."""
    store = ConversationStore(temp_db)
    store.append("chat_1", "user", "First")
    time.sleep(0.01)
    store.append("chat_1", "assistant", "Second")
    time.sleep(0.01)
    store.append("chat_1", "user", "Third")

    history = store.history("chat_1")
    assert len(history) == 3
    assert history[0].content == "First"
    assert history[1].content == "Second"
    assert history[2].content == "Third"


def test_chat_id_isolation(temp_db):
    """Test that different chats don't interfere."""
    store = ConversationStore(temp_db)
    store.append("chat_1", "user", "Chat 1 message")
    store.append("chat_2", "user", "Chat 2 message")

    history_1 = store.history("chat_1")
    history_2 = store.history("chat_2")

    assert len(history_1) == 1
    assert history_1[0].content == "Chat 1 message"
    assert len(history_2) == 1
    assert history_2[0].content == "Chat 2 message"


def test_reset(temp_db):
    """Test resetting conversation history."""
    store = ConversationStore(temp_db)
    store.append("chat_1", "user", "Hello")
    store.append("chat_1", "assistant", "Hi")

    history = store.history("chat_1")
    assert len(history) == 2

    store.reset("chat_1")

    history = store.history("chat_1")
    assert len(history) == 0


def test_reset_isolated(temp_db):
    """Test that reset only affects specified chat."""
    store = ConversationStore(temp_db)
    store.append("chat_1", "user", "Message 1")
    store.append("chat_2", "user", "Message 2")

    store.reset("chat_1")

    history_1 = store.history("chat_1")
    history_2 = store.history("chat_2")

    assert len(history_1) == 0
    assert len(history_2) == 1
    assert history_2[0].content == "Message 2"
