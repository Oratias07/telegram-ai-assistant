import sqlite3
import os
from typing import Optional


def init_db(db_path: str) -> None:
    """Initialize SQLite database with messages table."""
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            ts INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def get_connection(db_path: str) -> sqlite3.Connection:
    """Get a connection to SQLite database."""
    return sqlite3.connect(db_path)
