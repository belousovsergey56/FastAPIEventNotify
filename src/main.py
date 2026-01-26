import aiohttp

from fastapi import FastAPI, Depends
from services.api_kudago import get_events
from dependencies.http_client import get_aiohttp_session

app = FastAPI()

@app.get("/")
async def index(session: aiohttp.ClientSession = Depends(get_aiohttp_session)):
    return {"result": await get_events(session)}

    
