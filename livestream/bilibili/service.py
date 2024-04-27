import random
import threading
from dataclasses import dataclass
from typing import List

from bilibili_api import Credential, sync
from bilibili_api import Danmaku
from bilibili_api.live import LiveDanmaku
from loguru import logger

from common.abs_service import AbstractService, ServiceStatus
from config import GlobalConfig
from utils.datacls import Danmaku


@dataclass
class BilibiliServiceStatus(ServiceStatus):
    LISTENING = 'LISTENING'
    PAUSED = 'PAUSED'
    STOP = 'STOP'


class BilibiliService(AbstractService):
    def __init__(self, cfg: GlobalConfig):
        bili_cfg = cfg.live_stream.platforms[0]
        self._room_id = bili_cfg.room_id
        self._credential = Credential(sessdata=bili_cfg.sessdata, bili_jct=bili_cfg.bili_jct, buvid3=bili_cfg.buvid3)
        self._danmaku_list: List[Danmaku] = []
        # Bilibili live stream monitor
        self._monitor = LiveDanmaku(self._room_id, credential=self._credential)
        self._recv_event = threading.Event()
        self._running = False

    def start(self):

        self._running = True
        logger.info('Bilibili service starting...')

        @self._monitor.on("DANMU_MSG")
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

            self._add(danmaku)

        self._running = False
        sync(self._monitor.connect())
        logger.warning('Bilibili monitor disconnected.')

    def stop(self):
        self._running = False
        self._monitor.disconnect()
        logger.warning('Bilibili service stopped.')

    def pause(self):
        if self._recv_event.is_set():
            self._recv_event.clear()
            logger.warning('Bilibili service paused.')
        else:
            logger.warning('Invalid operation: Bilibili service has been paused.')

    def resume(self):
        if not self._recv_event.is_set():
            self._recv_event.set()
            logger.warning('Bilibili service resumed.')
        else:
            logger.warning('Invalid operation: Bilibili service has been resumed.')

    def status(self) -> BilibiliServiceStatus:
        if self._running:
            if self._recv_event.is_set():
                return BilibiliServiceStatus.LISTENING
            else:
                return BilibiliServiceStatus.PAUSED
        else:
            return BilibiliServiceStatus.STOP

    def _add(self, danmaku: Danmaku):
        # TODO: 这里可以实现多个过滤规则的运作
        self._danmaku_list.append(danmaku)
        logger.debug(f'添加 1 条弹幕于弹幕列表中，现在{len(self._danmaku_list)}')

    def select_latest_longest(self, k: int) -> Danmaku:
        # 按照某种策略拾取弹幕
        # 按照当前时间戳最近的k条中随机挑选msg字段字符串最长的一条（若都相同，则随机）

        # 选择出未读过的弹幕
        unread_danmaku_list = [danmaku for danmaku in self._danmaku_list if not danmaku.is_read]

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
