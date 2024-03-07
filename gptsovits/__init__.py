import os

import yaml
from loguru import logger

TMP_DIR: str
SERVER_URL: str


def load_config():
    """
        检查配置文件是否无误
        :return: 配置字典
    """
    # 读取配置文件

    logger.info('正在读取 GPTSoVITSServiceConfig……')

    if not os.path.exists('gptsovits/config.yaml'):
        logger.critical('配置文件缺失：gptsovits/config.yaml')
        exit()

    with open('gptsovits/config.yaml', mode='r', encoding='utf-8') as file:
        config: dict = yaml.safe_load(file)
        config = config.get('GPTSoVITSServiceConfig', None)

    if not config:
        logger.error('无法读取 GPTSoVITSServiceConfig，格式不正确')

    global TMP_DIR
    TMP_DIR = config.get('tmp_dir', r'gptsovits\.tmp')
    try:
        if not os.path.exists(TMP_DIR):
            os.mkdir(TMP_DIR)
            logger.info(f'临时目录创建成功：{TMP_DIR}')
    except Exception as e:
        logger.warning(f'配置文件指定的临时目录无法被创建，使用默认临时目录')

    TMP_DIR = os.path.abspath(TMP_DIR)
    host = config.get('host', '127.0.0.1')
    port = config.get('port', 9880)
    global SERVER_URL
    SERVER_URL = f"http://{host}:{port}"

    logger.info('GPT-SoVITS 服务配置文件加载完成')


def init_service(config):
    ...


config = load_config()
init_service(config)
