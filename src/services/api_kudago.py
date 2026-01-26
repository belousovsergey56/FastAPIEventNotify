# import sys
# import os
# import asyncio
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# import aiohttp
from src.core.config import config
# from src.dependencies.http_client import get_aiohttp_session
# from fastapi import Depends

def print_url():
    URL = f"{config.url_kuda_go}/{config.api_version}"
    print(URL)
    
    return URL
# async def get_events():
#     param = {
#             "page": 1,
#             "page_size": 2,
#             "location": "spb",
#             "fields": "title,site_url,publication_date",
#             "text_format": "text"
#             }
#     async with get_aiohttp_session(f"{URL}/lists", params=param) as resp:
#         return await resp.json()

# if __name__ == "__main__":
    # asyncio.run(get_events)
    # print(URL)
