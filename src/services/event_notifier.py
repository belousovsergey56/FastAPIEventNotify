from aiohttp import ClientSession
from src.services.api_kudago import collect_data
from src.services.api_telegram import send_message, send_image


def prepare_message(event: dict) -> str:
    """Подготовить сообщение
    Функция готовит текст сообщения для отправки в ТГ
    Args:
        event (dict): словарь с данными image, dates, source, name etc.
    Returns:
        str: Подготовленное сообщение, гле значение кажного ключа добавляется
        с новой строки
    """
    message = ""
    for key, value in event.items():
        if "image" == key:
            continue
        if len(value) == 0:
            continue
        if "dates" == key:
            message += f"Дата проведения: {value}\n"
            continue
        message += f"{value}\n"
    return message


async def post_event(
    session: ClientSession,
    chat_id: str,
    message: str,
    url_image: str=None
) -> None:
    """Отправить сообщение в ТГ
    Отправка сообщения в ТГ, с картинкой или без
    Args:
        session (ClientSession): http сессия
        chat_id (str): идентификатор чата
        message (str): текст сообщения
        url_image (str): адрес картики в сети или пустое значение
    """
    if url_image is None:
        await send_message(session, chat_id, message)
    else:
        await send_image(session, chat_id, url_image, message)


async def send_event_response(session: ClientSession, chat_id: str) -> None:
    """Подготовить и отправить сообщение
    Выполняется сбор данных, затем обработка, затем отправка сообщения в ТГ
    Args:
        session (ClientSession): http сессия
        chat_id (str): идентификатор чата
    """
    event_data = await collect_data(session)
    for event in event_data:
        message = prepare_message(event)
        await post_event(session, chat_id, message, event.get("image"))
