import functools
import logging
import time
import inspect

logger = logging.getLogger(__name__)


def log_debug(func):
    func_name = func.__name__

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if inspect.iscoroutinefunction(func):

            async def async_wrapper():
                start_time = time.perf_counter()
                logger.debug(f"Вызов (async) {func_name}, аргументы {args} {kwargs}")
                try:
                    result = await func(*args, **kwargs)
                    exec_time = time.perf_counter() - start_time
                    logger.debug(f"Завершено {func_name} за {exec_time:.4f}с")
                    return result
                except Exception as e:
                    logger.error(f"Ошибка в {func_name}: {e}", exc_info=True)
                    raise

            return async_wrapper()
        else:
            start_time = time.perf_counter()
            logger.debug(f"Вызов (sync) {func_name}")
            try:
                result = func(*args, **kwargs)
                exec_time = time.perf_counter() - start_time
                logger.debug(f"Завершено {func_name} за {exec_time:.4f}с")
                return result
            except Exception as e:
                logger.error(f"Ошибка в {func_name}: {e}", exc_info=True)
                raise

    return wrapper
