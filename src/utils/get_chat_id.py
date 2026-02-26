import functools
from src.core.context import chat_id_ctx_var

def inject_chat_id(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        if request:
            try:
                body = await request.json()
                message = body.get("message") or body.get("callback_query", {}).get("message")
                if message:
                    chat_id = str(message.get("chat", {}).get("id"))
                    chat_id_ctx_var.set(chat_id)
            except Exception:
                pass
        return await func(*args, **kwargs)
    return wrapper
