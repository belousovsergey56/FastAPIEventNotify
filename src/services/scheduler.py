from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.core.config import config
from src.database.crud import get_chat_list
from src.database.session import async_session
from src.services.event_notifier import prepare_message, post_event
from src.services.api_kudago import collect_data
from src.utils.debug_logs import log_debug


@log_debug
async def background_notification():
    """Фоновая рассылка
    Функция используется планировщиком, чтобы в фоновом режиме
    осуществлять рассылку с событиями на текущий день.
    """
    async with ClientSession(timeout=config.get_timeout()) as session:
        async with async_session() as db:
            chats = await get_chat_list(db)

        if not chats:
            print("Нет чатов")
            return

        events_list = await collect_data(session)

        for event in events_list:
            message = prepare_message(event)
            img_url = event.get("image")
            for chat in chats:
                chat_id = chat.chat_id
                try:
                    await post_event(session, chat_id, message, img_url)
                except Exception as e:
                    print(f"Сообщение не отправлено. Чат: {chat_id}, {e}")


scheduler = AsyncIOScheduler()
