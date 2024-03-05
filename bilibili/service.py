from dataclasses import dataclass
from typing import List

from bilibili_api import Danmaku, sync
from loguru import logger

from bilibili import MONITOR


@dataclass
class Danmaku:
    is_read: bool  # 弹幕是否被阅读过
    uid: str  # 弹幕发送者UID
    username: str  # 弹幕发送者名称
    msg: str  # 弹幕发送内容
    ts: int  # 弹幕时间戳


# 弹幕队列
danmaku_list: List[Danmaku] = []


def select(strategy):
    # 按照某种策略拾取弹幕
    # e.g. 按照当前时间戳最近的5条中随机挑选最长的一条
    danmaku = ...
    danmaku.is_read = True
    if ...:
        return danmaku
    return None


def add(danmaku: Danmaku):
    # TODO: 这里可以实现多个过滤规则的运作

    danmaku_list.append(danmaku)
    logger.debug(f'添加 1 条弹幕于弹幕列表中，现在{len(danmaku_list)}')


@MONITOR.on("DANMU_MSG")
async def recv(event):
    danmaku = Danmaku(uid=event["data"]["info"][2][0],
                      username=event["data"]["info"][2][1],
                      msg=event["data"]["info"][1],
                      ts=event["data"]["info"][9]['ts'],
                      is_read=False)
    # 注意没带粉丝牌的会导致越界
    # fans_band_level = event["data"]["info"][3][0]  # 粉丝牌的级别
    # fans_band_name = event["data"]["info"][3][1]  # 该粉丝牌的名字
    # live_host_name = event["data"]["info"][3][2]  # 该粉丝牌对应的主播名字

    logger.info(f'[{danmaku.username}]({danmaku.uid}): {danmaku.msg}')

    add(danmaku)
    # if main.is_audio_player_empty():
    #     model_req = ModelRequest(
    #         sys_prompt='你是一只猫娘。',
    #         query=f'{danmaku.msg}',
    #         top_p=1.,
    #         temperature=1.,
    #         history=[])
    #     response = requests.post(url=f'http://{CentralControllerConfig.host}:{CentralControllerConfig.port}/query',
    #                              json=asdict(model_req))
    #     danmaku_list.clear()


# 启动监听
def start():
    logger.info('Bilibili 直播间监听启动')
    sync(MONITOR.connect())
