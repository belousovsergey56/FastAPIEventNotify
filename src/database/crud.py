from src.models.chats import Chat
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def create_chat_id(db_session: AsyncSession, chat_id: int) -> Chat:
    new_chat = Chat(chat_id=chat_id)
    db_session.add(new_chat)
    await db_session.commit()
    await db_session.refresh(new_chat)
    return new_chat


async def read_chat(db_session: AsyncSession, chat_id: int) -> Chat | None:
    return await db_session.get(Chat, chat_id)


async def delete_chat(db_session: AsyncSession, chat_id: int) -> bool:
    get_chat = await read_chat(db_session, chat_id)
    if not get_chat:
        return False
    await db_session.delete(get_chat)
    await db_session.commit()
    return True


async def get_chat_list(db_session: AsyncSession) -> list[Chat]:
    chat_list = await db_session.execute(select(Chat))
    return list(chat_list.scalars().all())
