from aiohttp import ClientSession


class HttpClient:
    session: ClientSession = None


http_client = HttpClient()


async def get_aiohttp_session() -> ClientSession:
    """
    Возвращает общую асинхронную HTTP-сессию.

    Используется как зависимость (Dependency) в эндпоинтах FastAPI.
    Сессия управляется жизненным циклом приложения (lifespan), что позволяет
    переиспользовать TCP-соединения (connection pooling) и ускорять запросы.

    Returns:
        aiohttp.ClientSession: Глобальный объект асинхронной сессии.
    """
    return http_client.session
