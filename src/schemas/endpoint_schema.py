from pydantic import BaseModel
from typing import Optional


class AddToDBSchema(BaseModel):
    result: Optional[str] = "added"
    chat_id: int
