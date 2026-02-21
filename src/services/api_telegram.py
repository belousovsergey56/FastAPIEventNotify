import aiohttp

from src.core.config import config
from src.schemas.tg_schema import CheckBotSchema

URL = f"{config.tg_url}/bot{config.tg_token}"



async def check_bot(session: aiohttp.ClientSession) -> CheckBotSchema:
    """Проверить токен
    Протой тест на проверку валидности токена и
    что бот жив и настроен.
    Returns:
        dict:
            {
                'ok': True,
                'result':
                {
                    'id': 13345678910,
                    'is_bot': True,
                    'first_name': 'event_notify',
                    'username': 'some_bot',
                    'can_join_groups': True,
                    'can_read_all_group_messages': True,
                    'supports_inline_queries': False,
                    'can_connect_to_business': False,
                    'has_main_web_app': False
                    }
                }
    """
    async with session.get(f"{URL}/getMe") as resp:
        raw = await resp.json()
        return raw


async def send_message(session: aiohttp.ClientSession, chat_id: str, message: str):
    """Отправить сообщение
    Функция отправки сообщения на ресурс - в чат бот
    Args:
        chat_id (str): идентификатор чата
        message (str): сообщение, котрое отправляем в чат
    Returns:
        dict: возвращается словарь
    """
    url = f"{URL}/sendMessage"
    param = {
            "chat_id": chat_id,
            "text": message,
            }
    async with session.post(url, json=param) as resp:
        raw = await resp.json()
        print(raw)
    return raw


async def send_image(
    session: aiohttp.ClientSession,
    chat_id: str,
    image_url: str,
    caption_text: str
):
    """Отправить фото с подписью
    Args:
        chat_id (str): идентификатор чата
        image_url (str): урл адрес картинки
        caption_text (str): пост в 1024 символа и короткая подпись
    """
    url = f"{URL}/sendPhoto"
    param = {
            "chat_id": chat_id,
            "photo": image_url,
            "caption": caption_text
            }
    async with session.post(url, data=param) as resp:
        raw = await resp.json()
    return raw


async def set_webhook(session: aiohttp.ClientSession, https_url: str):
    param = {
            "url": f"{https_url}/webhook"
            }
    url = f"{URL}/setWebhook"
    async with session.post(url, json=param) as resp:
        raw = await resp.json()
    return raw
