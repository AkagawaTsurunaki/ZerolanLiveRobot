from functools import wraps
from time import time

from loguru import logger

from config import GLOBAL_CONFIG as G_CFG


class InitError(Exception):
    def __init__(self, message):
        super().__init__(self)
        self.message = message

    def __str__(self):
        return self.message


def llm_loading_log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        model_name = G_CFG.large_language_model.models[0].model_name
        try:
            logger.info(f'💭 模型 {model_name} 正在加载……')
            time_start = time()
            ret = func(*args, **kwargs)
            time_end = time()
            time_used = "{:.2f}".format(time_end - time_start)
            logger.info(f'💭 模型 {model_name} 加载完毕，用时 {time_used} 秒。')
            return ret
        except AssertionError:
            logger.critical(f'❌️ 模型 {model_name} 加载失败。')

    return wrapper


def img_cap_loading_log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        model_name = G_CFG.image_captioning.models[0].model_name
        try:
            logger.info(f'👀 模型 {model_name} 正在加载……')
            time_start = time()
            ret = func(*args, **kwargs)
            time_end = time()
            time_used = "{:.2f}".format(time_end - time_start)
            logger.info(f'👀 模型 {model_name} 加载完毕，用时 {time_used} 秒。')
            return ret
        except AssertionError:
            logger.critical(f'❌️ 模型 {model_name} 加载失败。')

    return wrapper
