from contextvars import ContextVar
import uuid

chat_id_ctx_var: ContextVar[str] = ContextVar("chat_id", default="")
