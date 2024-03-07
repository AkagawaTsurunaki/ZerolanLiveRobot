import os

import yaml
from bilibili_api import Credential
from bilibili_api.live import LiveDanmaku, LiveRoom
from loguru import logger

CREDENTIAL: Credential
MONITOR: LiveDanmaku
SENDER: LiveRoom


def load_config():
    """
    检查配置文件是否无误
    :return: 配置字典
    """
    # 读取配置文件

    logger.info('正在读取 BilibiliLiveConfig……')

    if not os.path.exists('bilibili/config.yaml'):
        logger.critical('配置文件缺失：bilibili/config.yaml')
        exit()

    with open('bilibili/config.yaml', mode='r', encoding='utf-8') as file:
        config: dict = yaml.safe_load(file)
        config = config.get('BilibiliLiveConfig', None)

    if not config:
        logger.error('无法读取 BilibiliLiveConfig，格式不正确')

    if not config.get('SESSDATA'):
        logger.error('BilibiliLiveConfig 中的 SESSDATA 字段不能为 None')
        return

    if not config.get('bili_jct'):
        logger.error('BilibiliLiveConfig 中的 bili_jct 字段不能为 None')
        return

    if not config.get('buvid3'):
        logger.error('BilibiliLiveConfig 中的 buvid3 字段不能为 None')
        return

    logger.info(f'直播间 ID：{config.get("room_id")}')

    return config


def init_service(config):
    # 凭证，根据回复弹幕的账号填写

    SESSDATA = config.get('SESSDATA', None)
    bili_jct = config.get('bili_jct', None)
    buvid3 = config.get('buvid3', None)
    room_id = config.get('room_id', None)

    global CREDENTIAL, MONITOR, SENDER
    CREDENTIAL = Credential(
        sessdata=SESSDATA,
        bili_jct=bili_jct,
        buvid3=buvid3
    )

    # 监听直播间弹幕
    MONITOR = LiveDanmaku(room_id, credential=CREDENTIAL)
    # 用来发送弹幕
    SENDER = LiveRoom(room_id, credential=CREDENTIAL)


config = load_config()
init_service(config)
