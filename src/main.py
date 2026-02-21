import aiohttp
import asyncio
import sys
import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse, Response
from src.dependencies.http_client import get_aiohttp_session
from src.dependencies.database import get_db
from src.database.crud import create_chat_id, delete_chat, get_chat_list, read_chat
from src.models.chats import Chat
from src.services.api_telegram import check_bot, send_message, set_webhook
from src.services.event_notifier import send_event_response
from src.services.scheduler import scheduler, background_notification
from src.schemas.tg_schema import CheckBotSchema
from src.schemas.endpoint_schema import AddToDBSchema
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """Фоновая задача
     Фоновая задача, запускаемая вместе с FastAPI приложением,
     останавливается, когда останавливается приложение.
     Данная функция запускает планировщик задач, который будет работать в фоне.
     Args:
         app (FastAPI): эксемпляр приложения FastAPI   
    """
    scheduler.add_job(background_notification, "cron", hour=12, minute=0)
    scheduler.start()
    print("Планировщик запущен\n")
    yield
    scheduler.shutdown()
    print("Планировщик остановлен\n")


app = FastAPI(
    title="FastAPI Event notify",
    lifespan=lifespan
)


@app.get("/", response_model=CheckBotSchema)
async def index(
    session: aiohttp.ClientSession = Depends(get_aiohttp_session)
) -> CheckBotSchema:
    """Главная страница\n
    Основная стараница возвращает результат CheckBotSchema
    """
    result: CheckBotSchema = await check_bot(session)
    return CheckBotSchema(**result)


@app.post("/add/{chat_id}", response_model=AddToDBSchema, responses={
              409: {"description": "Идентификатор уже существует"},
              500: {"description": "Ошибка при добавлении в базу"}
          })
async def add_chat(
    chat_id: int,
    session: AsyncSession = Depends(get_db)
) -> AddToDBSchema:
    """Добавить id чата в базу"""
    new_chat: Chat = await create_chat_id(session, chat_id)
    return AddToDBSchema(chat_id=new_chat.chat_id)


@app.delete("/delete_chat/{chat_id}",
            status_code=204,
            responses={404: {"description": "Не найден идентификатор для удаления"}})
async def deleted_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
) -> Response:
    """Удалить чат из базы"""
    deleted = await delete_chat(db, chat_id)
    if deleted:
        return Response(status_code=204)
    return Response(status_code=404)


@app.get("/read_chat/{chat_id}", status_code=200, responses={
             200: {"description": "Успешное чтение базы"},
             404: {"description": "Идентификатор отсутвует в базе"},
         })
async def get_chat(chat_id: int, db: AsyncSession = Depends(get_db)):
    """Получить данные по id из базы"""
    data_chat = await read_chat(db, chat_id)
    return {"result": data_chat}


@app.get("/chat_list", response_model=list[int], responses={
             200: {"description": "Успешное обращение к базе"},
             500: {"description": "Ошибка при обращении к базе"}
         },
         status_code=200)
async def chat_list(db: AsyncSession = Depends(get_db)) -> list[int]:
    """Получить список id чатов"""
    return [i.chat_id for i in await get_chat_list(db)]


@app.post("/webhook")
async def webhook(
    request: Request,
    session: aiohttp.ClientSession = Depends(get_aiohttp_session),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """Основное взаимодействие с телеграм чатом"""
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
    """Точка входа, запуск программы"""
    url_web_hook = sys.argv[1:]
    tuna_url = url_web_hook if len(url_web_hook) > 0 else "https://127.0.0.1"
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
