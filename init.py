import os
from loguru import logger

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


gen_temp_dir()
logger.info("Zerolan Live Robot 初始化完毕")