import time
from dataclasses import dataclass
from typing import Optional
from app.store.db import get_connection


@dataclass
class Message:
    role: str
    content: str
    ts: int


class ConversationStore:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def append(self, chat_id: str, role: str, content: str) -> None:
        """Append message to conversation history."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        ts = int(time.time())
        cursor.execute(
            "INSERT INTO messages (chat_id, role, content, ts) VALUES (?, ?, ?, ?)",
            (chat_id, role, content, ts),
        )
        conn.commit()
        conn.close()

    def history(self, chat_id: str, max_turns: int = 12) -> list[Message]:
        """Get last N turns (chronological order, oldest first)."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content, ts, id FROM messages WHERE chat_id = ? ORDER BY id ASC",
            (chat_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        messages = [Message(role=r[0], content=r[1], ts=r[2]) for r in rows]
        limit = max_turns * 2
        if len(messages) > limit:
            messages = messages[-limit:]
        return messages

    def reset(self, chat_id: str) -> None:
        """Clear conversation history for chat."""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        conn.commit()
        conn.close()
