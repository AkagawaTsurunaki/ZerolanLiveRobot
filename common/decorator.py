import json
from functools import wraps
from time import time
from typing import Callable

from loguru import logger

from services.device.speaker import Speaker


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


def withsound(sound: str, block: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            Speaker.play_system_sound(sound, block)
            ret = func(*args, **kwargs)
            return ret

        return wrapper

    return decorator


def pipeline_resolve():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
                return ret
            except Exception as e:
                if isinstance(e, json.decoder.JSONDecodeError):
                    logger.error("""
                    Pipeline encountered an error when decode JSON content, please try:
                    1. Check your connection to your zerolan-core server.
                    2. Maybe you need authentication to your server.
                    3. Just enter the url in your browser and see what happened.
                    """)
                raise e

        return wrapper

    return decorator
