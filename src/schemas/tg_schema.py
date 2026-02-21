from pydantic import BaseModel
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
