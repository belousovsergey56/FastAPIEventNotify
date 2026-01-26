from pydantic_settings import BaseSettings
from pydantic import SettingsConfigDict


class Settings(BaseSettings):
    url: str
    timeout: int = 30
    url_kuda_go: str
    api_version: str
    tg_url: str
    tg_token: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


config = Settings()
