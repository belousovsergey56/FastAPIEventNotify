import aiohttp

from asyncio import gather
from datetime import datetime
from src.core.config import config
from src.schemas.kudago_schema import (
    SchemaGetEvents,
    SchemaGetPlaces,
    SchemaGetCollections,
    SchemaGetMovieList,
    SchemaGetNews,
)
from src.utils.debug_logs import log_debug


@log_debug
def to_unixtime() -> int:
    """Получить текущее время в unixtime формате.
    Returns:
        int: 1763715782 unixtime формат, целое число
    """
    return int(datetime.now().timestamp())


@log_debug
def to_datetime(unixtime: int) -> str:
    """Преобразовать unixtime в datetime.
    Returns:
        str: возвращается строка вормате "2025-11-21 12:12:25"
    """
    return str(datetime.fromtimestamp(unixtime))


@log_debug
def date_event(dates: list[dict[str, int]]) -> str:
    """Преобразовать список дат в строку
    Обходит список дат, преобразует из unixtime в datetime и сохраняет в строку
    Args:
        dates (list): список словарей с датами
        [
        {'end': 1622448000, 'start': 1618732800},
        {'end': 1633593600, 'start': 1633593600},
        {'end': 1633692600, 'start': 1633692600},
        ...
        ]
    Returns:
        str: С 2025-12-13 00:00:00 по 2026-01-12 00:00:00
    """
    result = []
    now_unix = int(datetime.now().timestamp())

    for date_dict in dates:
        start_unix = date_dict.get("start")
        if start_unix is None or start_unix < now_unix:
            continue
        end_unix = date_dict.get("end", start_unix)

        start_dt = datetime.fromtimestamp(start_unix)
        end_dt = datetime.fromtimestamp(end_unix)
        result.append(f"С {start_dt} по {end_dt}")

    return "\n".join(result) if result else ""


@log_debug
async def get_events(session: aiohttp.ClientSession) -> SchemaGetEvents:
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
        "text_format": "text",
    }
    url = config.get_full_url()
    async with session.get(f"{url}/events", params=param) as resp:
        raw = await resp.json()
    return SchemaGetEvents(**raw)


@log_debug
async def get_places(
    session: aiohttp.ClientSession, place_id: int | None
) -> SchemaGetPlaces:
    """Получить назвние и адрес места по id.
    Args:
        place_id (int): id места
    Returns:
        dict: Возвращает словарь с адресом, именем места
            {
              "count": 1,
              "next": null,
              "previous": null,
              "results": [
                {
                  "id": 336,
                  "title": "клуб А2",
                  "address": "просп. Медиков, д. 3"
                }
              ]
            }
    """
    if place_id is None:
        return {}
    param = {
        "page": 1,
        "page_size": 1,
        "fields": "id,title,address",
        "text_format": "text",
        "ids": place_id,
    }
    url = config.get_full_url()
    async with session.get(f"{url}/places", params=param) as resp:
        raw = await resp.json()
    return SchemaGetPlaces(**raw)


@log_debug
async def get_collections(session: aiohttp.ClientSession) -> SchemaGetCollections:
    """Получить список подборок редакции
    При тестировании от текущей даты, апи
    возвращает только две актуальных подборки.
    Returns:
        dict: Возвращает словарь с результатами по событиям
            {
              "count": 1626,
              "next": "https://kudago.com/public-api/v1.4/lists/?fields=title%2Csite_url&location=spb&page=2&page_size=2&text_format=text",
              "previous": null,
              "results": [
                {
                  "title": "Где в Петербурге научиться рисовать",
                  "site_url": "https://kudago.com/spb/list/gde-v-peterburge-nauchitsya/"
                },
                {
                  "title": "Главные номинанты премии «Оскар—2026»",
                  "site_url": "https://kudago.com/all/list/glavnyie-nominantyi-premii-oskar-2026/"
                }
              ]
            }
    """
    param = {
        "page": 1,
        "page_size": 2,
        "location": "spb",
        "fields": "title,site_url",
        "text_format": "text",
    }
    url = f"{config.get_full_url()}/lists"
    async with session.get(url, params=param) as resp:
        raw = await resp.json()
    return SchemaGetCollections(**raw)


@log_debug
async def get_movie_list(session: aiohttp.ClientSession) -> SchemaGetMovieList:
    """Получить список фильмов.
        Функция возвращает список словарей в колличестве
        трёх штук, где есть описание фильма, его название,
        дата публикации и ссылка на постер.
        Returns:
            dict: Пример возвращаемого словаря
    {
      "count": 36,
      "next": "https://kudago.com/public-api/v1.4/movies/?actual_since=1770113358&fields=id%2Ctitle%2Cdescription%2Cimages&location=spb&page=2&page_size=3&text_format=text",
      "previous": null,
      "results": [
        {
          "id": 6681,
          "title": "Код: Неизвестен",
          "description": "Фильм Михаэля Ханеке о случайности как движущей силе современного мира.",
          "images": [
            {
              "image": "https://media.kudago.com/images/movie/d2/da/d2dac04c5db3daf02497964eb9b7fe69.webp",
              "source": {
                "name": "kinopoisk.ru",
                "link": "https://www.kinopoisk.ru/film/18342/stills/page/1/"
              }
            },
            {
              "image": "https://media.kudago.com/images/movie/ec/1d/ec1d1b592f5ae538968326588426a9df.webp",
              "source": {
                "name": "kinopoisk.ru",
                "link": "https://www.kinopoisk.ru/film/18342/stills/page/1/"
              }
            },
          ]
      ]
    }
    }
    """
    param = {
        "page": 1,
        "page_size": 3,
        "fields": "id,title,description,images",
        "location": "spb",
        "text_format": "text",
        "actual_since": to_unixtime(),
    }
    url = f"{config.get_full_url()}/movies"
    async with session.get(url, params=param) as resp:
        raw = await resp.json()
    return SchemaGetMovieList(**raw)


@log_debug
async def get_news(session: aiohttp.ClientSession) -> SchemaGetNews:
    """Получить новости на сегодняшний день
    Returns:
        dict: Пример вывода
        {'count': 1231,
        'next': 'https://kudago.com/public-api/v1.4/news/?actual_only=True&fields=publication_date%2Ctitle%2Cdescription%2Cimages%2Csite_url&location=spb&page=2&page_size=1',
        'previous': None,
        'results': [{'description': '<p>Каждый календарный день — это целый '
                             'калейдоскоп праздников, за которыми стоят самые '
                             'разнообразные истории, традиции и смыслы. 24 '
                             'ноября на первый взгляд кажется ничем не '
                             'примечательной датой, но стоит заглянуть глубже '
                             '— и перед нами откроется удивительный мир, '
                             'наполненный как древними языческими обрядами, '
                             'так и современными социальными движениями. От '
                             'Домового, пьющего молоко, до торжеств в честь '
                             'японской кухни — всё это празднуется именно в '
                             'этот день</p>',
              'images': [{'image': 'https://media.kudago.com/images/news/e2/08/e2087378c9b65efd72483499222d970c.jpg',
                          'source': {'link': 'https://www.shutterstock.com/ru/image-photo/closeup-walrus-odobenus-rosmarus-colony-on-2359243961',
                                     'name': 'LouieLea/FOTODOM/Shutterstock'}}],
              'publication_date': 1763932208,
              'site_url': 'https://kudago.com/all/news/24-noyabrya-kakoj-prazdnik/',
              'title': '24 ноября: какой праздник сегодня'}]}
    """
    param = {
        "page": 1,
        "page_size": 1,
        "fields": "title,description,images,site_url",
        "actual_only": 1,
        "location": "spb",
        "text_format": "text",
    }
    url = f"{config.get_full_url()}/news"
    async with session.get(url, params=param) as resp:
        raw = await resp.json()
    return SchemaGetNews(**raw)


@log_debug
async def process_collect_data(
    session: aiohttp.ClientSession, data: list[dict]
) -> list[dict]:
    """Формирует полученные данные в список
    Полученные данные по событиям, подготавливает и добавляет в список
    Args:
        session (ClientSession): http сессия
        data (list[dict]): сырой список словарей с событиями
    Returns:
        list[dict]: обработанный список словарей с событиями
    """
    data_list = []
    for result in data:
        # Список мероприятий
        if isinstance(result, SchemaGetCollections):
            for collect in result.results:
                collect = collect.model_dump()
                data_list.append(
                    {"title": collect.get("title"), "site_url": collect.get("site_url")}
                )
        # Список событий
        if isinstance(result, SchemaGetEvents):
            for events in result.results:
                event = events.model_dump()
                try:
                    place_id = event.get("place").get("id")
                    place = await get_places(session, place_id)
                    place = place.model_dump().get("results")[0]
                    place = f"{place.get("title")}, {place.get("address")}"
                except (TypeError, AttributeError, IndexError):
                    place = ""

                data_list.append(
                    {
                        "title": event.get("title"),
                        "description": event.get("description"),
                        "place": place,
                        "price": event.get("price"),
                        "image": event.get("images")[0].get("image"),
                        "dates": date_event(event.get("dates")),
                    }
                )
        # список фильмов
        if isinstance(result, SchemaGetMovieList):
            for movie in result.results:
                movie = movie.model_dump()
                data_list.append(
                    {
                        "title": movie.get("title"),
                        "description": movie.get("description"),
                        "image": movie.get("images")[0].get("image"),
                    }
                )
        # список новостей
        if isinstance(result, SchemaGetNews):
            for tidings in result.results:
                tidings = tidings.model_dump()
                data_list.append(
                    {
                        "title": tidings.get("title"),
                        "description": tidings.get("description"),
                        "image": tidings.get("images")[0].get("image"),
                        "site_url": tidings.get("site_url"),
                    }
                )
    return data_list


async def collect_data(session: aiohttp.ClientSession) -> list[dict]:
    """Получаяет события, обрабатывает и возвращает списком"""
    result = await gather(
        get_collections(session),
        get_events(session),
        get_movie_list(session),
        get_news(session),
    )
    return await process_collect_data(session, result)
