import time

from loguru import logger

from common.decorator import log_run_time


@log_run_time(time_limit=5)
def slow_function():
    """
    模拟一个运行较慢的函数
    """
    time.sleep(10)  # 模拟耗时操作
    return "Task completed"


@log_run_time(time_limit=5)
def fast_function():
    """
    模拟一个运行较快的函数
    """
    time.sleep(2)  # 模拟耗时操作
    return "Task completed quickly"


def test_slow_func():
    logger.info("Starting slow function")
    result = slow_function()
    logger.info(result)


def test_fast_func():
    logger.info("Starting fast function")
    result = fast_function()
    logger.info(result)
