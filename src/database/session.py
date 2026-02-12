from src.core.config import config
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    async_sessionmaker,
    create_async_engine,
    )

engine = create_async_engine(
    config.get_db_url(),
    echo=True,
    future=True
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncConnection,
    expire_on_commit=False
)
