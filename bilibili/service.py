import os
import random
from dataclasses import dataclass
from typing import List

import yaml
from bilibili_api import Credential
from bilibili_api import Danmaku
from bilibili_api.live import LiveDanmaku, LiveRoom
from loguru import logger


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

    credential = Credential(
        sessdata=SESSDATA,
        bili_jct=bili_jct,
        buvid3=buvid3
    )

    # 监听直播间弹幕
    monitor = LiveDanmaku(room_id, credential=credential)
    # 用来发送弹幕
    sender = LiveRoom(room_id, credential=credential)
    return monitor, sender


config = load_config()
monitor, sender = init_service(config)


@dataclass
class Danmaku:
    is_read: bool  # 弹幕是否被阅读过
    uid: str  # 弹幕发送者UID
    username: str  # 弹幕发送者名称
    msg: str  # 弹幕发送内容
    ts: int  # 弹幕时间戳


# 弹幕队列
danmaku_list: List[Danmaku] = []


def select_01(k: int) -> Danmaku:
    # 按照某种策略拾取弹幕
    # 按照当前时间戳最近的k条中随机挑选msg字段字符串最长的一条（若都相同，则随机）

    # 选择出未读过的弹幕
    unread_danmaku_list = [danmaku for danmaku in danmaku_list if not danmaku.is_read]

    # 如果弹幕数小于k
    if len(unread_danmaku_list) < k:
        selected_danmaku = max(unread_danmaku_list, key=lambda danmaku: len(danmaku.msg), default=None)
    # 如果弹幕数大于k
    else:
        recent_danmakus = sorted(unread_danmaku_list, key=lambda danmaku: danmaku.ts, reverse=True)[:k]
        max_length = max(len(danmaku.msg) for danmaku in recent_danmakus)
        longest_danmakus = [danmaku for danmaku in recent_danmakus if len(danmaku.msg) == max_length]
        selected_danmaku = random.choice(longest_danmakus) if longest_danmakus else None
    # 将选择的弹幕标记为已读
    if selected_danmaku:
        selected_danmaku.is_read = True
    return selected_danmaku


def add(danmaku: Danmaku):
    # TODO: 这里可以实现多个过滤规则的运作

    danmaku_list.append(danmaku)
    logger.debug(f'添加 1 条弹幕于弹幕列表中，现在{len(danmaku_list)}')


@monitor.on("DANMU_MSG")
async def recv(event):
    logger.debug('asdhkajsdhjks')
    danmaku = Danmaku(uid=event["data"]["info"][2][0],
                      username=event["data"]["info"][2][1],
                      msg=event["data"]["info"][1],
                      ts=event["data"]["info"][9]['ts'],
                      is_read=False)
    # 注意没带粉丝牌的会导致越界
    # fans_band_level = event["data"]["info"][3][0]  # 粉丝牌的级别
    # fans_band_name = event["data"]["info"][3][1]  # 该粉丝牌的名字
    # live_host_name = event["data"]["info"][3][2]  # 该粉丝牌对应的主播名字

    logger.info(f'🍥 [{danmaku.username}]({danmaku.uid}): {danmaku.msg}')

    add(danmaku)


# 启动监听
async def start():
    logger.info('Bilibili 直播间监听启动')
    await monitor.connect()