from src.models.chats import Chat
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def create_chat_id(session: AsyncSession, chat_id: int) -> Chat:
    new_chat = Chat(chat_id=chat_id)
    session.add(new_chat)
    await session.commit()
    await session.refresh(new_chat)
    return new_chat


async def read_chat(session: AsyncSession, chat_id: int) -> Chat | None:
    return await session.get(Chat, chat_id)


async def delete_chat(session: AsyncSession, chat_id: int) -> bool:
    get_chat = await read_chat(session, chat_id)
    if not get_chat:
        return False
    await session.delete(get_chat)
    await session.commit()
    return True


async def get_chat_list(session: AsyncSession) -> list[Chat]:
    chat_list = await session.execute(select(Chat))
    return list(chat_list.scalars().all())
