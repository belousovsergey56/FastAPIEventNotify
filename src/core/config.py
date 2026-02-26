import aiohttp
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PrivateAttr, model_validator
from pathlib import Path

BASE_DIR = Path(".").resolve()

class Settings(BaseSettings):
    """Основные настройки приложения"""
    url_kuda_go: str
    api_version: str
    tg_url: str
    tg_token: str
    timeout: int = 60
    db_url: str
    _client_timeout: aiohttp.ClientTimeout = PrivateAttr(default=None)
    log_level: str = "INFO"
    log_file_path: str = "src/logs/app.logs"
    log_max_bytes: int = 5 * 1024 * 1024
    log_backup_count: int = 3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    def get_full_url(self) -> str:
        """Полный URL к API KudaGo с учетом версии."""
        return f"{self.url_kuda_go.rstrip("/")}/{self.api_version}"

    def get_timeout(self) -> aiohttp.ClientTimeout:
        """Объект таймаута для aiohttp."""
        return self._client_timeout

    @model_validator(mode="after")
    def init_timeout(self) -> "Settings":
        """
        Инициализирует объект ClientTimeout после загрузки настроек.
        
        Этот метод берет значение из поля `timeout` (целое число секунд) и 
        конвертирует его в специальный объект `aiohttp.ClientTimeout`. 
        Это необходимо, так как библиотека aiohttp требует именно объект 
        для управления лимитами времени на разных этапах HTTP-запроса 
        (установление соединения, чтение данных и т.д.).
        """
        self._client_timeout = aiohttp.ClientTimeout(total=self.timeout)
        return self

config = Settings()
