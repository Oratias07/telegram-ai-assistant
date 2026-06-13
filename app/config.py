from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    telegram_bot_token: str
    groq_api_key: str
    database_path: str = "./bot.db"


def load_settings() -> Settings:
    return Settings()
