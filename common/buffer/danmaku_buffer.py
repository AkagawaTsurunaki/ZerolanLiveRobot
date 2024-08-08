import random
from dataclasses import dataclass
from typing import List

from common.buffer.asb_buf import AbstractBuffer, BufferObject
from services.live_stream.pipeline import Danmaku


@dataclass
class DanmakuBufferObject(BufferObject):
    def __init__(self, danmaku: Danmaku):
        super().__init__()
        self.danmaku: Danmaku = danmaku


class DanmakuBuffer(AbstractBuffer):

    def __init__(self):
        super().__init__()
        self._buffer: List[DanmakuBufferObject] = []

    def select_latest_longest(self, k: int) -> DanmakuBufferObject:
        # 按照某种策略拾取弹幕
        # 按照当前时间戳最近的k条中随机挑选msg字段字符串最长的一条（若都相同，则随机）

        # 选择出未读过的弹幕
        unread_danmaku_list: List[DanmakuBufferObject] = [dbo for dbo in self._buffer if not dbo.is_processed]

        # 如果弹幕数小于k
        if len(unread_danmaku_list) < k:
            selected_danmaku: DanmakuBufferObject = max(unread_danmaku_list, key=lambda dbo: len(dbo.danmaku.msg),
                                                        default=None)
        # 如果弹幕数大于k
        else:
            recent_danmakus = sorted(unread_danmaku_list, key=lambda dbo: dbo.danmaku.ts, reverse=True)[:k]
            max_length = max(len(dbo.danmaku.msg) for dbo in recent_danmakus)
            longest_danmakus = [danmaku for danmaku in recent_danmakus if len(danmaku.danmaku.msg) == max_length]
            selected_danmaku: DanmakuBufferObject = random.choice(longest_danmakus) if longest_danmakus else None
        # 将选择的弹幕标记为已读
        if selected_danmaku:
            selected_danmaku.is_processed = True
        return selected_danmaku
