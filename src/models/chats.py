from datetime import datetime
from src.models.base import Base
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class Chat(Base):
    chat_id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
