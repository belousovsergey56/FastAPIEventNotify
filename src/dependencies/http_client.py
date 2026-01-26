import aiohttp

from src.core.config import Settings


setting = Settings()

async def get_aiohttp_session() -> aiohttp.ClientSession:
    async with aiohttp.ClientSession(timeout=setting.timeout) as session:
        yield session
