from pydantic import BaseModel, Field
from typing import Optional


class CheckBotResult(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: str
    can_join_groups: bool
    can_read_all_group_messages: bool
    supports_inline_queries: bool
    can_connect_to_business: bool
    has_main_web_app: bool
    has_topics_enabled: bool


class CheckBotSchema(BaseModel):
    ok: bool
    result: Optional[CheckBotResult] = None
    error_code: Optional[int] = None
    desctiption: Optional[str] = None


class WebHookSchema(BaseModel):
    ok: bool
    result: Optional[bool] = None
    description: str
    error_code: Optional[int] = None


class FromBot(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: Optional[str]


class ChatData(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    type: str


class SendResult(BaseModel):
    message_id: int
    from_bot: FromBot = Field(..., alias="from")
    chat: ChatData
    date: int


class TextMessageResult(SendResult):
    text: str


class SendMessageSchema(BaseModel):
    ok: bool
    result: TextMessageResult


class PhotoSize(BaseModel):
    file_id: str
    file_unique_id: str
    file_size: int
    width: int
    height: int


class SendPhotoResult(SendResult):
    photo: list[PhotoSize]
    caption: Optional[str] = None


class SendPhotoSchema(BaseModel):
    ok: bool
    result: SendPhotoResult
