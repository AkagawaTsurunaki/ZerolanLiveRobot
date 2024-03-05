import json

from loguru import logger

from gptsovits.common import Config

tmp_dir = './gptsovits/.tmp'


def read_config(default_config_path: str):
    try:
        with open(file=default_config_path, mode='r', encoding='utf-8') as f:
            config_dict = json.load(fp=f)
            config = Config(**config_dict)
            return config
    except Exception as e:
        logger.warning(e)
        return None


