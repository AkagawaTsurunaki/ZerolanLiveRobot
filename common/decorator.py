from functools import wraps
from time import time
from typing import Callable

from loguru import logger


def log_model_loading(model_info):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.info(f'模型 {model_info.id} 正在加载……')
                time_start = time()
                ret = func(*args, **kwargs)
                time_end = time()
                time_used = "{:.2f}".format(time_end - time_start)
                logger.info(f'模型 {model_info.id} 加载完毕，用时 {time_used} 秒。')
                return ret
            except AssertionError as e:
                logger.exception(e)
                logger.critical(f'模型 {model_info.id} 加载失败。')

        return wrapper

    return decorator


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
