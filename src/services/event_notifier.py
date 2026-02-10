from aiohttp import ClientSession
from src.services.api_kudago import collect_data
from src.services.api_telegram import send_message, send_image


def prepare_message(event: dict) -> str:
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
):
    if url_image is None:
        await send_message(session, chat_id, message)
    else:
        await send_image(session, chat_id, url_image, message)


async def send_event_response(session: ClientSession, chat_id: str):
    event_data = await collect_data(session)
    for event in event_data:
        message = prepare_message(event)
        await post_event(session, chat_id, message, event.get("image"))
