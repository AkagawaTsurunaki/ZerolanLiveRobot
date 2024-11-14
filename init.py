import multiprocessing
from multiprocessing import Process

from loguru import logger
from zerolan.ui import app


def start_ui_process() -> Process:
    process = multiprocessing.Process(target=app.start_ui_application)
    process.start()

    logger.info("等待UI进程启动……")

    return process
