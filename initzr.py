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
    assert os.path.exists(
        default_global_config_path), f'❌️ 全局配置文件不存在：路径 {default_global_config_path} 不存在。'
    global_config = read_yaml(path=default_global_config_path)
    logger.info('⚙️ 全局配置加载完毕')
    return global_config


def load_bilibili_live_config(global_config: dict) -> (str, str, str, int):
    """
    加载 Bilibili 直播配置
    :return: tuple 包含 sessdata, bili_jct, buvid3, room_id（直播间 ID）四个配置项
    :raises AssertionError: 如果配置项缺失或格式有误
    """
    bilibili_live_config = global_config.get('bilibili_live_config', None)
    assert bilibili_live_config, f'❌️ Bilibili 直播配置未填写或格式有误'
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


def load_screenshot_config(global_config: dict) -> (str, int, str | PathLike):
    """

    :param global_config:
    :return:
    """
    screenshot_config = global_config.get('screenshot_config', None)
    assert screenshot_config, f'❌️ 截屏配置未填写或格式有误'
    win_title = screenshot_config.get('win_title', None)
    assert win_title, f'❌️ 截屏配置中的字段 win_title 未填写或格式有误'
    k = screenshot_config.get('k', 0.9)
    assert 0 < k < 1, f'❌️ 截屏配置中的字段 win_title 必须在 0 ~ 1 之间'
    save_dir = screenshot_config.get('save_dir', '.tmp/screenshots')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
        logger.warning(f'⚠️ 截屏配置中的字段 save_dir 所指向的目录不存在，已自动创建')
    assert os.path.isdir(save_dir), f'❌️ 截屏配置中的字段 save_dir 所指向的路径不是一个目录'
    logger.info('⚙️ 截屏配置加载完毕')
    return win_title, k, save_dir


def load_blip_image_captioning_large_config(global_config: dict) -> (str | PathLike, str):
    """
    加载模型 blip-image-captioning-large 的配置
    :param global_config:
    :return:
    """
    blip_image_captioning_large_config = global_config.get('blip_image_captioning_large_config', None)
    assert blip_image_captioning_large_config, f'❌️ 模型 blip-image-captioning-large 配置未填写或格式有误'
    model_path = blip_image_captioning_large_config.get('model_path')
    if not os.path.exists(model_path):
        model_path = 'Salesforce/blip-image-captioning-large'
    text_prompt = blip_image_captioning_large_config.get('text_prompt', 'There')
    logger.info('⚙️ 模型 blip-image-captioning-large 配置加载完毕')
    return model_path, text_prompt


def load_gpt_sovits_config(global_config: dict) -> (bool, str, int, str | PathLike, bool):
    gpt_sovits_config = global_config.get('gpt_sovits_service_config', None)
    assert gpt_sovits_config, f'❌️ GPT-SoVITS 服务配置未填写或格式有误'
    debug = gpt_sovits_config.get('debug', False)
    host = gpt_sovits_config.get('host', '127.0.0.1')
    port = gpt_sovits_config.get('port', 9880)
    save_dir = gpt_sovits_config.get('save_dir', '.tmp/wav_output')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
        logger.warning('⚠️ GPT-SoVITS 服务配置中的字段 save_dir 所指向的目录不存在，已自动创建')
    clean = gpt_sovits_config.get('clean', False)
    logger.info('⚙️ GPT-SoVITS 服务配置加载完毕')
    return debug, host, port, save_dir, clean
