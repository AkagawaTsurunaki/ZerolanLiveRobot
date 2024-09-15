import multiprocessing
import os
from multiprocessing import Process

import requests
from loguru import logger
from retry import retry

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


def check(url: str):
    response = requests.get(url)
    if response.json()["status"] != "ok":
        raise ValueError()


def start_ui_process() -> Process:
    """
    启动 UI 进程。如果 UI 进程未启动，将会尝试启动。如果 UI 进程已经启动，那么将不会进行任何操作。

    Returns:
        是否已经启动；UI handler

    """
    process = multiprocessing.Process(target=app.start_ui_application)
    process.start()

    logger.info("等待UI进程启动……")

    @retry(tries=10, delay=1)
    def check_ui():
        check(url="http://127.0.0.1:5000/status")

    check_ui()

    return process
