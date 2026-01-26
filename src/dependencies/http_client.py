import aiohttp

from src.core.config import config
from typing import AsyncGenerator


async def get_aiohttp_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    async with aiohttp.ClientSession(timeout=config.get_timeout()) as session:
        yield session
