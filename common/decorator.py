import json
from functools import wraps
from multiprocessing import Process
from time import time

from loguru import logger
from zerolan.ui import app

from common.enumerator import SystemSoundEnum
from services.device.speaker import Speaker


def log_run_time():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            time_start = time()
            ret = func(*args, **kwargs)
            time_end = time()
            time_used = "{:.2f}".format(time_end - time_start)
            logger.info(func.__name__ + "time used: " + time_used + " s.")
            return ret

        return wrapper

    return decorator


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


_ui_process: Process | None = None


def start_ui_process(enable: bool):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if enable:
                global _ui_process
                _ui_process = Process(target=app.start_ui_application, daemon=True)
                _ui_process.start()
                logger.info("Zerolan UI Process started.")
            ret = func(*args, **kwargs)
            # process.join()
            return ret

        return wrapper

    return decorator


def kill_ui_process(force: bool):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global _ui_process
            if _ui_process is None:
                return func(*args, **kwargs)

            if force:
                _ui_process.kill()
                _ui_process.terminate()
            else:
                app.shutdown()
                _ui_process.terminate()
            _ui_process.join()
            logger.info("Zerolan UI Process stopped.")
            return func(*args, **kwargs)

        return wrapper

    return decorator
