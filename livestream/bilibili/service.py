import copy
import threading
from typing import List

from bilibili_api import Credential, sync
from bilibili_api import Danmaku
from bilibili_api.live import LiveDanmaku
from loguru import logger

from common.datacls import Danmaku, BilibiliServiceStatus
from config import GlobalConfig

_monitor: LiveDanmaku
_recv_event: threading.Event
_danmaku_list: List[Danmaku] = []
_running: bool


def init(cfg: GlobalConfig):
    global _monitor, _recv_event, _danmaku_list, _running
    bili_cfg = cfg.live_stream.platforms[0]
    room_id = bili_cfg.room_id
    credential = Credential(sessdata=bili_cfg.sessdata, bili_jct=bili_cfg.bili_jct, buvid3=bili_cfg.buvid3)
    _danmaku_list = []
    # Bilibili live stream monitor
    _monitor = LiveDanmaku(room_id, credential=credential)
    _recv_event = threading.Event()
    _running = False


def start():
    global _running, _danmaku_list
    _running = True
    logger.info('Bilibili service starting...')

    @_monitor.on("DANMU_MSG")
    async def recv(self, event):
        danmaku = Danmaku(uid=event["data"]["info"][2][0],
                          username=event["data"]["info"][2][1],
                          msg=event["data"]["info"][1],
                          ts=event["data"]["info"][9]['ts'],
                          is_read=False)
        # 注意没带粉丝牌的会导致越界
        # fans_band_level = event["data"]["info"][3][0]  # 粉丝牌的级别
        # fans_band_name = event["data"]["info"][3][1]  # 该粉丝牌的名字
        # live_host_name = event["data"]["info"][3][2]  # 该粉丝牌对应的主播名字

        logger.debug(f'🍥 [{danmaku.username}]({danmaku.uid}): {danmaku.msg}')

        _add(danmaku)

    _running = False
    sync(_monitor.connect())
    logger.warning('Bilibili monitor disconnected.')


def _add(danmaku: Danmaku):
    # TODO: 这里可以实现多个过滤规则的运作
    _danmaku_list.append(danmaku)
    logger.debug(f'添加 1 条弹幕于弹幕列表中，现在{len(_danmaku_list)}')


def stop():
    global _running
    _running = False
    _monitor.disconnect()
    logger.warning('Bilibili service stopped.')


def pause():
    if _recv_event.is_set():
        _recv_event.clear()
        logger.warning('Bilibili service paused.')
    else:
        logger.warning('Invalid operation: Bilibili service has been paused.')


def resume():
    if not _recv_event.is_set():
        _recv_event.set()
        logger.warning('Bilibili service resumed.')
    else:
        logger.warning('Invalid operation: Bilibili service has been resumed.')


def status() -> BilibiliServiceStatus:
    if _running:
        if _recv_event.is_set():
            return BilibiliServiceStatus.LISTENING
        else:
            return BilibiliServiceStatus.PAUSED
    else:
        return BilibiliServiceStatus.STOP


def all_danmakus():
    return copy.deepcopy(_danmaku_list)
