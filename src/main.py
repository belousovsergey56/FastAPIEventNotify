import aiohttp

from fastapi import FastAPI, Depends
from services.api_kudago import get_events, get_places, get_collections, get_movie_list, get_news
from schemas.kudado_schema import SchemaGetEvents, SchemaGetPlaces, SchemaGetCollections, SchemaGetMovieList, SchemaGetNews
from dependencies.http_client import get_aiohttp_session

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
