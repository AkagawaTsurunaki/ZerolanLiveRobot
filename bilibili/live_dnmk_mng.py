from dataclasses import dataclass, asdict
from typing import List

import requests
from bilibili_api import Credential, Danmaku, sync
from bilibili_api.live import LiveDanmaku, LiveRoom
from loguru import logger

import cookie
import main
from chatglm3.common import ModelRequest
from config import CentralControllerConfig


@dataclass
class Danmaku:
    uid: str  # 弹幕发送者UID
    username: str  # 弹幕发送者名称
    msg: str  # 弹幕发送内容
    ts: int  # 弹幕时间戳


# 凭证 根据回复弹幕的账号填写
credential = Credential(
    sessdata=cookie.SESSDATA,
    bili_jct=cookie.bili_jct,
    buvid3=cookie.buvid3
)
# 监听直播间弹幕
monitor = LiveDanmaku(CentralControllerConfig.room_id, credential=credential)
# 用来发送弹幕
sender = LiveRoom(CentralControllerConfig.room_id, credential=credential)
# 自己的UID 可以手动填写也可以根据直播间号获取
UID = sync(sender.get_room_info())["room_info"]["uid"]
sys_prompt = CentralControllerConfig.sys_prompt

# 弹幕队列
danmaku_list: List[Danmaku] = []


@monitor.on("DANMU_MSG")
async def recv(event):
    danmaku = Danmaku(uid=event["data"]["info"][2][0],
                      username=event["data"]["info"][2][1],
                      msg=event["data"]["info"][1],
                      ts=event["data"]["info"][9]['ts'])
    # 注意没带粉丝牌的会导致越界
    # fans_band_level = event["data"]["info"][3][0]  # 粉丝牌的级别
    # fans_band_name = event["data"]["info"][3][1]  # 该粉丝牌的名字
    # live_host_name = event["data"]["info"][3][2]  # 该粉丝牌对应的主播名字
    # 排除自己发送的弹幕
    if danmaku.uid == UID:
        return

    logger.info(f'[{danmaku.username}]({danmaku.uid}): {danmaku.msg}')

    if main.is_audio_player_empty():
        logger.debug('空了')
        model_req = ModelRequest(
            sys_prompt=sys_prompt,
            query=f'{danmaku.msg}',
            top_p=1.,
            temperature=1.,
            history=[])
        response = requests.post(url=f'http://{CentralControllerConfig.host}:{CentralControllerConfig.port}/query',
                                 json=asdict(model_req))
        danmaku_list.clear()


# 启动监听
def start():
    logger.info('Bilibili 直播间监听启动')
    sync(monitor.connect())
