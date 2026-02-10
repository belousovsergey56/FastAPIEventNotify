import aiohttp
import asyncio
import sys
import uvicorn

from fastapi import FastAPI, Depends
from fastapi import Request
from fastapi.responses import JSONResponse
from src.dependencies.http_client import get_aiohttp_session
from src.services.api_telegram import check_bot, send_message, set_webhook
from src.services.event_notifier import send_event_response


app = FastAPI()


@app.get("/")
async def index(session: aiohttp.ClientSession = Depends(get_aiohttp_session)):
    result = await check_bot(session)
    return {
        "ok": "Сервер запущен",
        "check_bot": result,
        }


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
                await send_event_response(session, chat_id)
            elif tg_message == "/delete":
                # если id удалён из базы
                await send_message(session, chat_id, "Рассылка отменена")
                # если нет
                # send_message(chat_id, "В списке рассылок нет текущего чата")
            elif tg_message == "/event":
                await send_message(session, chat_id, "Собираем данные о событиях, минуту...")
                await send_event_response(session, chat_id)
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
  
# async def main():    
#     uvicorn.run(
#         "src.main:app",
#         host="0.0.0.0",
#         port=5000,
#         reload=True
#     )
if __name__ == "__main__":
    asyncio.run(main())
