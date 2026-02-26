import logging
from fastapi import HTTPException
from src.models.chats import Chat
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, delete

logger = logging.getLogger(__name__)

async def create_chat_id(
    db_session: AsyncSession,
    chat_id: int
) -> Chat | HTTPException:
    """Добавить чат id в базу
    Args:
        db_session (AsyncSession): сессия для работы с базой
        chat_id (int): идентификато чата
    Returns:
        Chat:
            chat_id: chat_id
            created_at: YYYY-MM_DDTHH:MM:SS
        HTTPException: Ошибки 409 или 500
    """
    new_chat = Chat(chat_id=chat_id)
    db_session.add(new_chat)
    try:
        await db_session.commit()
        await db_session.refresh(new_chat)
        logger.info(f"Successfully added new chat to database: {chat_id}")
        return new_chat
    except IntegrityError:
        await db_session.rollback()
        logger.warning(f"Attempt to add duplicate chat_idAttempt to add duplicate chat_id {chat_id}")
        raise HTTPException(
            status_code=409,
            detail=f"Идентификатор чата {chat_id} уже существует"
        )
    except Exception:
        await db_session.rollback()
        logger.error(f"ailed to create chat {chat_id} due to unexpected error")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при добавлении в базу"
        )


async def read_chat(
    db_session: AsyncSession,
    chat_id: int
) -> Chat | HTTPException:
    """Прочитать из базы по идентификатору чата
    Args:
        db_session (AsyncSession): сессия для работы с базой
        chat_id (int): идентификатор чата
    Returns:
        Chat:
            chat_id: chat_id
            created_at: YYYY-MM_DDTHH:MM:SS
        HTTPException: Ошибка 404
    """
    chat = await db_session.get(Chat, chat_id)
    if chat is None:
        raise HTTPException(
                status_code=404,
                detail=f"Чат с идентификатором {chat_id} отсутствует в базе"
            )
    return chat


async def delete_chat(db_session: AsyncSession, chat_id: int) -> bool:
    """Удалить чат
    Args:
        db_session (AsyncSession): сессия для работы с базой
        chat_id (int): идентификатор чата
    Returns:
        bool: True если успех, False если ошибка

    """
    try:
        stmt = delete(Chat).where(Chat.chat_id == chat_id)
        result = await db_session.execute(stmt)
        await db_session.commit()
        return result.rowcount > 0
    except Exception:
        await db_session.rollback()
        return False


async def get_chat_list(db_session: AsyncSession) -> list[Chat]:
    """Получить список чатов
    Args:
        db_session (AsyncSession): сессия для работы с базой
    Returns:
        list[Chats]:
            [{
                chat_id: chat_id,
                created_at: YYYY-MM_DDTHH:MM:SS
            },]        
    """
    try:
        chat_list = await db_session.execute(select(Chat))
        return list(chat_list.scalars().all())
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Ошибка при обращении к базе"
        )
