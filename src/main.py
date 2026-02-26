import aiohttp
import sys
import uuid
import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse, Response
from src.core.config import config
from src.core.logger_setup import setup_app_logging
from src.core.context import chat_id_ctx_var
from src.dependencies.http_client import get_aiohttp_session, http_client
from src.dependencies.database import get_db
from src.database.crud import create_chat_id, delete_chat, get_chat_list, read_chat
from src.models.chats import Chat
from src.services.api_telegram import check_bot, send_message, set_webhook
from src.services.event_notifier import send_event_response
from src.services.scheduler import scheduler, background_notification
from src.schemas.tg_schema import CheckBotSchema
from src.schemas.endpoint_schema import AddToDBSchema
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.get_chat_id import inject_chat_id

@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """Управление ресурсами"""
    listener = setup_app_logging()
    listener.start()
    header = {
        "User-Agent": "FastAPIEventNotifyBot/1.0",
        "Accept": "application/json",
    }
    http_client.session = aiohttp.ClientSession(
                                timeout=config.get_timeout(),
                                headers=header
                            )
    webhook_url = sys.argv[1] if len(sys.argv) > 1 else "https://127.0.0.1"
    try:
        status = await set_webhook(http_client.session, webhook_url)
        print(f"Вебхук установлен: {webhook_url}. Статус: {status}")
    except Exception as e:
        print(f"Ошибка установки вебхука: {e}")

    scheduler.add_job(background_notification, "cron", hour=12, minute=0)
    scheduler.start()
    print("Планировщик запущен\n")
    try:
        yield
    finally:
        await http_client.session.close()
        scheduler.shutdown()
        print("Планировщик остановлен\n")
        listener.stop()

app = FastAPI(
    title="FastAPI Event notify",
    lifespan=lifespan
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # 1. Генерируем или берем ID
    chat_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    # 2. Устанавливаем в контекст (важно для логгера)
    token = chat_id_ctx_var.set(chat_id)
    try:
        # 3. Передаем управление дальше по цепочке
        response = await call_next(request)
        # 4. Добавляем ID в ответ для клиента
        response.headers["X-Request-ID"] = chat_id
        return response
    finally:
        # 5. Обязательно сбрасываем контекст
        chat_id_ctx_var.reset(token)


@app.get("/", response_model=CheckBotSchema)
async def index(
    session: aiohttp.ClientSession = Depends(get_aiohttp_session)
) -> CheckBotSchema:
    """Главная страница\n
    Основная стараница возвращает результат CheckBotSchema
    """
    result: CheckBotSchema = await check_bot(session)
    return result


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
            responses={
                404: {"description": "Не найден идентификатор для удаления"},
                204: {"description": "Чат удалён"}
            })
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
@inject_chat_id
async def webhook(
    request: Request,
    session: aiohttp.ClientSession = Depends(get_aiohttp_session),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """Основное взаимодействие с телеграм чатом"""
    try:
        payload = await request.json()
        if "message" in payload:
            chat_id_ctx_var.set(payload["message"]["chat"]["id"])
            chat_id = payload["message"]["chat"]["id"]
            tg_message = payload["message"]["text"]
            if tg_message == "/start":
                try:
                    await create_chat_id(db, chat_id)
                    await send_message(
                                   session,
                                   chat_id,
                                   "Чат добавлен в расписание, события каждый день")
                    await send_message(session, chat_id, "Подготовка первых событий")
                    await send_event_response(session, chat_id)
                except HTTPException as e:
                    if e.status_code == 409:
                        await send_message(session, chat_id, "Чат в расписание уже был добавлен")
                    else:
                        raise e
            elif tg_message == "/delete":
                deleted = await delete_chat(db, chat_id)
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


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
