from pydantic import BaseModel
from typing import List


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
    result: CheckBotResult
