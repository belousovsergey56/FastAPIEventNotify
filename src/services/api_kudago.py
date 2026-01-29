import aiohttp
import time

from datetime import datetime
from src.core.config import config
from src.schemas.kudado_schema import SchemaEventValidator

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def to_unixtime() -> int:
    """Получить текущее время в unixtime формате.
    Returns:
        int: 1763715782 unixtime формат, целое число 
    """
    return int(time.mktime(datetime.now().timetuple()))


def to_datetime(unixtime: int) -> str:
    """Преобразовать unixtime в datetime.
    Returns:
        str: возвращается строка вормате "2025-11-21 12:12:25" 
    """
    return str(datetime.fromtimestamp(unixtime))


async def get_events(session: aiohttp.ClientSession) -> SchemaEventValidator:
    """Получить список мероприятий
    Returns:
        dict: Возвращается словарь 
        в котором есть ключ results, это список
        словарей с событиями
        {
    "count": 82677,
    "next": "https://kudago.com/public-api/v1.2/events/?fields=age_restriction%2Cis_free&page=2",
    "previous": null,
    "results": [
        "results": [
      {
        "dates": [
          {
            "start": -62135433000,
            "end": 253370754000
          }
        ],
        "description": "Камерная экскурсия, которая оставит вас наедине с мыслями ленинградцев в осаждённом городе. Прогулка построена на основе записок и ценна тем, что воспоминаниями о блокаде пережившие её люди делились неохотно. Начните экскурсию тогда, когда будете готовы.",
        "images": [
          {
            "image": "https://media.kudago.com/images/event/b5/f8/b5f81286943a865cc5eac9a17e5914f2.jpg",
            "source": {
              "name": "spbzoo.ru",
              "link": "http://www.spbzoo.ru/o_nas/istoriya-zooparka/poslevoennoe-vosstanovlenie/"
            }
          }
        ],
        "place": {
          "id": 3037
        },
        "title": "Аудиоэкскурсия «Блокада на Петроградской стороне с Софьей Лурье»",
        "price": ""
      }
    ]
}
    """
    param = {
            "page": 1,
            "page_size": 5,
            "fields": "images,dates,title,place,description,price",
            "location": "spb",
            "actual_since": to_unixtime(),
            "text_format":"text"
            }
    url = config.get_full_url()
    async with session.get(f"{url}/events", params=param) as resp:
        raw = await resp.json()
    return SchemaEventValidator(**raw)
