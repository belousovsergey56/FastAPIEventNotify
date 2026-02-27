from src.database.session import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Создает и управляет асинхронной сессией базы данных.

    Используется как зависимость (Dependency) в эндпоинтах FastAPI.
    Гарантирует закрытие сессии после завершения обработки запроса,
    даже в случае возникновения исключений.

    Yields:
        AsyncSession: Объект асинхронной сессии SQLAlchemy.
    """
    async with async_session() as session:
        yield session
