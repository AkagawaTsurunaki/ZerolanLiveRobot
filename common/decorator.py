import json
import threading
from functools import wraps

from loguru import logger

from common.enumerator import SystemSoundEnum
from services.device.speaker import Speaker


def withsound(sound: SystemSoundEnum, block: bool = False):
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
                    """.strip())
                elif isinstance(e, ConnectionError):
                    logger.error("""
                    Pipeline encountered an error when connect to zerolan-core, please try:
                    1. Check your connection to your zerolan-core server.
                    2. See your configuration for pipeline.
                    """)
                    # if e.
                raise e

        return wrapper

    return decorator


def log_init(service_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            logger.info(f"{service_name} initialized.")
            return ret

        return wrapper

    return decorator


def log_start(service_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"{service_name} starting...")
            ret = func(*args, **kwargs)
            logger.info(f"{service_name} exited.")
            return ret

        return wrapper

    return decorator


def log_stop(service_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"{service_name} stopping...")
            ret = func(*args, **kwargs)
            logger.info(f"{service_name} stopped.")
            return ret

        return wrapper

    return decorator


def log_run_time(time_limit=10):
    """
    装饰器：对函数进行实时计时，运行时间超过指定限制时实时打印警告。

    Args:
        time_limit (int): 时间限制（秒），默认为5秒。
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.perf_counter()
            # 标志函数是否完成
            finished = threading.Event()

            def check_duration():
                while not finished.is_set():
                    elapsed_time = time.perf_counter() - start_time
                    if elapsed_time > time_limit:
                        # 如果尚未发出警告，则发出警告
                        if not getattr(func, 'warned', False):
                            logger.warning(
                                f"Function {func.__name__} exceeded time limit. Time elapsed: {elapsed_time:.4f} seconds."
                            )
                            setattr(func, 'warned', True)
                    # 简单的延时，避免过度CPU占用
                    time.sleep(0.1)

            # 启动一个后台线程来检查运行时间
            monitor_thread = threading.Thread(target=check_duration, daemon=True)
            monitor_thread.start()

            try:
                result = func(*args, **kwargs)
            finally:
                # 标志函数已完成
                finished.set()

            elapsed_time = time.perf_counter() - start_time
            if not getattr(func, 'warned', False):
                logger.info(
                    f"Function {func.__name__} completed in {elapsed_time:.4f} seconds."
                )
            else:
                logger.warning(
                    f"Function {func.__name__} completed with warnings. Total duration: {elapsed_time:.4f} seconds."
                )

            return result

        return wrapper

    return decorator
