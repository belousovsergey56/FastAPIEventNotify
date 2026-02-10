import aiohttp
import asyncio
import sys
import uvicorn

from fastapi import FastAPI, Depends
from fastapi import Request
from fastapi.responses import JSONResponse
from src.dependencies.http_client import get_aiohttp_session
from src.schemas.kudago_schema import SchemaGetEvents, SchemaGetPlaces, SchemaGetCollections, SchemaGetMovieList, SchemaGetNews
from src.schemas.tg_schema import CheckBotSchema
from src.services.api_kudago import get_events, get_places, get_collections, get_movie_list, get_news, collect_data
from src.services.api_telegram import check_bot, send_message, set_webhook, send_image
from typing import List


app = FastAPI()


@app.get("/")
async def index(session: aiohttp.ClientSession = Depends(get_aiohttp_session)):
    result = await check_bot(session)
    return {
        "ok": "Сервер запущен",
        "check_bot": result,
        }

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


@app.post("/webhook")
async def webhook(
    request: Request,
    session: aiohttp.ClientSession = Depends(get_aiohttp_session)
) -> JSONResponse:
    try:
        payload = await request.json()
        if "message" in payload:
            chat_id = payload["message"]["chat"]["id"]
            tg_message = payload["message"]["text"]
            if tg_message == "/start":
                # проверка на наличие id чата в базе
                # если есть, то send_message(chat_id, "Чат в расписание уже был добавлен")
                # Иначе код ниже
                await send_message(
                                   session,
                                   chat_id,
                                   "Чат добавлен в расписание, события каждый день")
                # добавить chat_id в базу
                await send_message(session, chat_id, "Подготовка первых событий")
                # send_event_response(chat_id)
            elif tg_message == "/image":
                img_url = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimg.freepik.com%2Fpremium-photo%2Ffinish-text-written-yellow-line-road-middle-asphalt-road-business-planning-strategies-challenges-road-success-concept-finish-word-street_35148-5231.jpg%3Fsemt%3Dais_hybrid&f=1&nofb=1&ipt=f05c2d9230f35b4cb08cd0ee75739f4d583a2b20bae163c7d84daf578125bfba"
                await send_image(session, chat_id, img_url, "finish")
            elif tg_message == "/delete":
                # если id удалён из базы
                await send_message(session, chat_id, "Рассылка отменена")
                # если нет
                # send_message(chat_id, "В списке рассылок нет текущего чата")
            elif tg_message == "/event":
                await send_message(session, chat_id, "Собираем данные о событиях, минуту...")
                # await send_event_response(chat_id)
            elif tg_message == "/help":
                message = "/start - добавляет чат в расписание для ежедневной отправки сообщений о событияx\n"
                message += "/delete - убирает чат из расписания\n"
                message += "/event - подготавливает данные о событиях и однократно отправляет в чат\n"
                message += "/help - печатает это сообщение"
                await send_message(session, chat_id, message)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    return JSONResponse(status_code=200, content={"ok": "worked"})


async def main():
    tuna_url = sys.argv[1]
    async with aiohttp.ClientSession() as session:
        whook = await set_webhook(session, tuna_url)
        print(whook)
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
  

if __name__ == "__main__":
    asyncio.run(main())
