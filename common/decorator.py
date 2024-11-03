from functools import wraps
from time import time
from typing import Callable

from loguru import logger


def log_run_time(log: Callable[[str], str] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            time_start = time()
            ret = func(*args, **kwargs)
            time_end = time()
            time_used = "{:.2f}".format(time_end - time_start)
            logger.info(log(time_used) if log else f"用时 {time_used} 秒")
            return ret

        return wrapper

    return decorator


def playsound(path: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from manager.device.speaker import Speaker
            Speaker.playsound(path, block=False)
            ret = func(*args, **kwargs)
            return ret

        return wrapper

    return decorator
