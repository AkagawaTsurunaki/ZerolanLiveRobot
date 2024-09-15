import multiprocessing
import os
import time
from multiprocessing import Process

import requests
from loguru import logger

import app


def try_create_dir(dir_path: str):
    if not os.path.exists(dir_path):
        logger.info(f"由于目录 {dir_path} 不存在，将被创建")
        os.mkdir(dir_path)
    assert os.path.isdir(dir_path)


def gen_temp_dir():
    """
    生成存放数据的临时目录
    """
    current_work_dir = os.getcwd()
    data_dir = os.path.join(current_work_dir, "data")
    try_create_dir(data_dir)
    temp_dir = os.path.join(data_dir, "temp")
    try_create_dir(temp_dir)

    for dir_name in ["image", "audio", "video"]:
        dir_path = os.path.join(temp_dir, dir_name)
        try_create_dir(dir_path)


class UIHandler:
    def __init__(self, obj: Process | str):
        self.process = obj if isinstance(obj, Process) else None
        self.url = obj if isinstance(obj, str) else None

    def stop(self):
        if self.process is not None:
            self.process.kill()
            logger.info("已关闭 UI 进程。")
        elif self.url is not None:
            response = requests.get(f"{self.url}/shutdown")
            if response.json()["status"] == "shutdown":
                logger.info("已关闭 UI 进程。")
            else:
                logger.warning("未能成功关闭 UI 进程，请手动关闭。")
        else:
            logger.warning("Handler 不知如何处理这种状况，无法关闭 UI 进程。")


def start_ui_process(max_try_count=10, url="http://127.0.0.1:5000") -> (bool, UIHandler):
    """
    启动 UI 进程。如果 UI 进程未启动，将会尝试启动。如果 UI 进程已经启动，那么将不会进行任何操作。

    Args:
        url: UI 启动的URL
        max_try_count: 最大尝试次数

    Returns:
        是否已经启动；UI handler

    """

    def check():
        try:
            response = requests.get(f"{url}/status")
            if response.json()["status"] == "ok":
                return True
        except Exception:
            return False

    if not check():
        # 尝试启动
        process = multiprocessing.Process(target=app.start_ui_application)
        process.start()

        logger.info("等待UI进程启动……")

        try_count = 0
        while not check():
            time.sleep(1)
            try_count += 1
            if try_count > max_try_count:
                logger.error("UI 进程无法自动启动，请手动解决。")
                return False, UIHandler(process)

    logger.info("UI 进程已启动完毕")

    return True, UIHandler(url)


gen_temp_dir()
logger.info("Zerolan Live Robot 初始化完毕")
