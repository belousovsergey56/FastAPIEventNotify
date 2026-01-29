import aiohttp

from fastapi import FastAPI, Depends
from services.api_kudago import get_events
from schemas.kudado_schema import SchemaEventValidator
from dependencies.http_client import get_aiohttp_session
from typing import Dict

app = FastAPI()

@app.get("/")
async def index(session: aiohttp.ClientSession = Depends(get_aiohttp_session)) -> Dict[str, SchemaEventValidator]:
    result = await get_events(session)
    return {"result": result}

    
