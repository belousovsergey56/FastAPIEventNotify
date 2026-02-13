import aiohttp
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PrivateAttr, model_validator
from pathlib import Path

BASE_DIR = Path(".").resolve()

class Settings(BaseSettings):
    url_kuda_go: str
    api_version: str
    tg_url: str
    tg_token: str
    timeout: int = 30
    DATABASE_ENGINE: str = "sqlite+aiosqlite:///"
    DB_FILE: str = "database/chats.db"
    DB_URL: str = f"{DATABASE_ENGINE}src/{DB_FILE}"
    
    _client_timeout: aiohttp.ClientTimeout = PrivateAttr(default=None)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


    def get_db_url(self) -> str:
        db_path = BASE_DIR / self.DB_FILE
        if self.DATABASE_ENGINE.startswith(("sqlite", "aiosqlite")):
            return f"{self.DATABASE_ENGINE}{db_path}"
        else:
            return self.DATABASE_ENGINE

    def get_full_url(self) -> str:
        return f"{self.url_kuda_go}/{self.api_version}"

    def get_timeout(self) -> aiohttp.ClientTimeout:
        return self._client_timeout

    @model_validator(mode="after")
    def init_timeout(self) -> "Settings":
        self._client_timeout = aiohttp.ClientTimeout(total=self.timeout)
        return self

config = Settings()
