import os
from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    telegram_bot_token: str
    groq_api_key: str
    database_path: str = "./bot.db"

    def resolve_database_path(self) -> str:
        """Resolve database path to absolute, handling service mode."""
        db_path = Path(self.database_path)
        if db_path.is_absolute():
            return str(db_path)

        # If relative, resolve relative to repo root (parent of app/)
        repo_root = Path(__file__).parent.parent
        return str(repo_root / db_path)


def load_settings() -> Settings:
    repo_root = Path(__file__).parent.parent
    env_file = repo_root / ".env"
    return Settings(_env_file=env_file if env_file.exists() else None)
