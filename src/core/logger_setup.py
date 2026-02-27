import logging
import logging.handlers
import sys
from pythonjsonlogger import jsonlogger
from queue import Queue
from src.core.config import config


def setup_app_logging():
    log_format = (
        "%(asctime)s %(levelname)s %(name)s %(message)s %(module)s %(funcName)s"
    )
    formatter = jsonlogger.JsonFormatter(log_format, json_ensure_ascii=False)
    cli_formatter = logging.Formatter(fmt=log_format, datefmt="%H:%M:%S")

    filehandler = logging.handlers.RotatingFileHandler(
        filename=config.log_file_path,
        maxBytes=config.log_max_bytes,
        backupCount=config.log_backup_count,
        encoding="utf-8",
    )

    filehandler.setFormatter(formatter)
    filehandler.setLevel("INFO")

    cli_handler = logging.StreamHandler(sys.stdout)
    cli_handler.setFormatter(fmt=cli_formatter)
    cli_handler.setLevel("DEBUG")

    log_queue = Queue(-1)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    listener = logging.handlers.QueueListener(
        log_queue,
        filehandler,
        cli_handler,
        respect_handler_level=True,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(queue_handler)

    for logger_name in (None, "uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(logger_name)
        uv_logger.handlers = []
        uv_logger.addHandler(queue_handler)
        uv_logger.propagate = False

    return listener
