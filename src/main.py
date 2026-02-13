import aiohttp
import asyncio
import sys
import uvicorn

from fastapi import FastAPI, Depends
from fastapi import Request
from fastapi.responses import JSONResponse
from src.dependencies.http_client import get_aiohttp_session
from src.dependencies.database import get_db
from src.database.crud import create_chat_id, delete_chat, get_chat_list, read_chat
from src.services.api_telegram import check_bot, send_message, set_webhook
from src.services.event_notifier import send_event_response
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()


@app.get("/")
async def index(session: aiohttp.ClientSession = Depends(get_aiohttp_session)):
    result = await check_bot(session)
    
    return {
        "ok": "Сервер запущен",
        "check_bot": result,
        }

@app.post("/add/{chat_id}")
async def add_chat(chat_id: int, session: AsyncSession = Depends(get_db)):
    new_chat = await create_chat_id(session, chat_id)
    return {"result": "ok", "chat_id": new_chat.chat_id}


@app.delete("/delete_chat/{chat_id}")
async def deleted_chat(chat_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await delete_chat(db, chat_id)
    return {"result": deleted}


@app.get("/read_chat/{chat_id}")
async def get_chat(chat_id: int, db: AsyncSession = Depends(get_db)):
    data_chat = await read_chat(db, chat_id)
    return {"result": data_chat}


@app.get("/chat_list")
async def chat_list(db: AsyncSession = Depends(get_db)):
    return [i.chat_id for i in await get_chat_list(db)]


@app.post("/webhook")
async def webhook(
    request: Request,
    session: aiohttp.ClientSession = Depends(get_aiohttp_session),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    try:
        payload = await request.json()
        if "message" in payload:
            list_chat_id = [i.chat_id for i in await get_chat_list(db)]
            chat_id = payload["message"]["chat"]["id"]
            tg_message = payload["message"]["text"]
            if tg_message == "/start":
                if chat_id in list_chat_id:
                    await send_message(session, chat_id, "Чат в расписание уже был добавлен")
                else:
                    await create_chat_id(db, int(chat_id))
                    await send_message(
                                   session,
                                   chat_id,
                                   "Чат добавлен в расписание, события каждый день")
                    await send_message(session, chat_id, "Подготовка первых событий")
                    await send_event_response(session, chat_id)
            elif tg_message == "/delete":
                deleted = await delete_chat(db, int(chat_id))
                if deleted:
                    await send_message(session, chat_id, "Рассылка отменена")
                else:
                    await send_message(session, chat_id, "В списке рассылок нет текущего чата")
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
  

if __name__ == "__main__":
    asyncio.run(main())
