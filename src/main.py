import aiohttp
import uvicorn

from fastapi import FastAPI, Depends
from src.dependencies.http_client import get_aiohttp_session
from src.schemas.kudago_schema import SchemaGetEvents, SchemaGetPlaces, SchemaGetCollections, SchemaGetMovieList, SchemaGetNews
from src.schemas.tg_schema import CheckBotSchema
from src.services.api_kudago import get_events, get_places, get_collections, get_movie_list, get_news, collect_data
from src.services.api_telegram import check_bot
from typing import List


app = FastAPI()


@app.get("/")
def index():
    return {"ok": "Сервер запущен"}

@app.get("/events")
async def events(session: aiohttp.ClientSession = Depends(get_aiohttp_session)) -> SchemaGetEvents:
    result = await get_events(session)
    return result


@app.get("/places/{place_id}")
async def places(place_id: int=None, session: aiohttp.ClientSession = Depends(get_aiohttp_session)) -> SchemaGetPlaces:
    result = await get_places(session, place_id)
    return result

@app.get("/collections")
async def collections(session: aiohttp.ClientSession = Depends(get_aiohttp_session)) -> SchemaGetCollections:
    result = await get_collections(session)
    return result

@app.get("/movies")
async def movie_list(session: aiohttp.ClientSession = Depends(get_aiohttp_session)) -> SchemaGetMovieList:
    result = await get_movie_list(session)
    return result

@app.get("/news")
async def news(session: aiohttp.ClientSession = Depends(get_aiohttp_session)) -> SchemaGetNews:
    result = await get_news(session)
    return result

@app.get("/collect")
async def collect(session: aiohttp.ClientSession = Depends(get_aiohttp_session)) -> List:
    result = await collect_data(session)
    return result

@app.get("/check_bots")
async def check_bots(session: aiohttp.ClientSession = Depends(get_aiohttp_session)) -> CheckBotSchema:
    result = await check_bot(session)
    return result   


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
