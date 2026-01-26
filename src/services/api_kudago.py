import aiohttp

from src.core.config import config

async def get_events(session: aiohttp.ClientSession):
    param = {
            "page": 1,
            "page_size": 2,
            "location": "spb",
            "fields": "title,site_url,publication_date",
            "text_format": "text"
            }
    async with session.get(f"{config.get_full_url()}/lists", params=param) as resp:
        return await resp.json()
