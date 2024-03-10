import os
from os import PathLike

import yaml
from loguru import logger


def read_yaml(path: str | PathLike):
    with open(file=path, mode='r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def load_global_config(default_global_config_path: str | PathLike) -> dict:
    """
    加载全局配置
    :param default_global_config_path:
    :return:
    """
    assert os.path.exists(default_global_config_path), f'❌️ 全局配置文件不存在：路径 {default_global_config_path} 不存在。'
    global_config =  read_yaml(path=default_global_config_path)
    logger.info('⚙️ 全局配置加载完毕')
    return global_config


def load_bilibili_live_config(global_config: dict) -> (str, str, str, int):
    """
    加载 Bilibili 直播配置
    :return: tuple 包含 sessdata, bili_jct, buvid3, room_id（直播间 ID）四个配置项
    :raises AssertionError: 如果配置项缺失或格式有误
    """
    bilibili_live_config = global_config.get('bilibili_live_config', None)
    assert bilibili_live_config, f'❌️ Bilibili 直播配置未填写或格式有误，请您仔细检查配置文件后重试'
    sessdata = bilibili_live_config.get('sessdata', 'SESSDATA')
    assert sessdata != 'SESSDATA', f'❌️ bilibili_live_config 中的字段 sessdata 未填写或格式有误'
    bili_jct = bilibili_live_config.get('bili_jct', 'bili_jct')
    assert bili_jct != 'bili_jct', f'❌️ bilibili_live_config 中的字段 bili_jct 未填写或格式有误'
    buvid3 = bilibili_live_config.get('buvid3', 'buvid3')
    assert buvid3 != 'bili_jct', f'❌️ bilibili_live_config 中的字段 buvid3 未填写或格式有误'
    room_id = bilibili_live_config.get('room_id', 'room_id')
    assert room_id >= 0, f'❌️ bilibili_live_config 中的字段 room_id 应当是一个非负 int 型整数'
    logger.info('⚙️ Bilibili 直播配置加载完毕')
    return sessdata, bili_jct, buvid3, room_id
