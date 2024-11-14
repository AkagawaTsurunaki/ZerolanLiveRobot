from functools import wraps
from time import time
from typing import Callable

from loguru import logger

from common.enum import SystemSoundEnum
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


def withsound(sound: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            Speaker.play_system_sound(sound)
            ret = func(*args, **kwargs)
            return ret
        return wrapper
    return decorator

def with_error_throw(e_type: type):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                ret = await func(*args, **kwargs)
                return ret
            except e_type as e:
                Speaker.play_system_sound(SystemSoundEnum.error)
                raise e
        return wrapper
    return decorator