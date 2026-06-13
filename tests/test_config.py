import os
import pytest
from pydantic import ValidationError
from app.config import Settings


def test_settings_load_from_env(tmp_path, monkeypatch):
    """Test that settings loads from environment variables."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "TELEGRAM_BOT_TOKEN=test_token_123\n"
        "GROQ_API_KEY=test_groq_key_456\n"
        "DATABASE_PATH=/tmp/test.db\n"
    )

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token_123")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key_456")
    monkeypatch.setenv("DATABASE_PATH", "/tmp/test.db")

    settings = Settings()
    assert settings.telegram_bot_token == "test_token_123"
    assert settings.groq_api_key == "test_groq_key_456"
    assert settings.database_path == "/tmp/test.db"


def test_settings_default_database_path(monkeypatch):
    """Test that DATABASE_PATH defaults to ./bot.db."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")

    settings = Settings()
    assert settings.database_path == "./bot.db"


def test_settings_missing_required_field(monkeypatch):
    """Test that missing required fields raise ValidationError."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_case_insensitive(monkeypatch):
    """Test that env var loading is case-insensitive."""
    monkeypatch.setenv("telegram_bot_token", "test_token")
    monkeypatch.setenv("groq_api_key", "test_groq_key")

    settings = Settings()
    assert settings.telegram_bot_token == "test_token"
    assert settings.groq_api_key == "test_groq_key"
