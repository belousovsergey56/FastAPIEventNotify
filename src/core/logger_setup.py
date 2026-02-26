import logging
import logging.handlers
from pythonjsonlogger import jsonlogger
from queue import Queue
from src.core.config import config
from src.core.context import chat_id_ctx_var


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.chat_id = chat_id_ctx_var.get()
        return True

def setup_app_logging():
    rid_filter = RequestIdFilter()
    log_format = "%(asctime)s %(levelname)s %(name)s %(chat_id)s %(message)s %(module)s %(funcName)s"
    formatter = jsonlogger.JsonFormatter(log_format)
    filehandler = logging.handlers.RotatingFileHandler(
        filename=config.log_file_path,
        maxBytes=config.log_max_bytes,
        backupCount=config.log_backup_count,
        encoding="utf-8"
    )
    filehandler.setFormatter(formatter)
    
    log_queue = Queue(-1)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    listener = logging.handlers.QueueListener(log_queue, filehandler)


    root_logger = logging.getLogger()
    root_logger.setLevel(config.log_level)
    root_logger.addFilter(rid_filter)
    root_logger.addHandler(queue_handler)

    for logger_name in (None, "uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(logger_name)
        uv_logger.handlers = []
        uv_logger.addFilter(rid_filter)
        uv_logger.addHandler(queue_handler)
        uv_logger.propagate = False

    return listener
