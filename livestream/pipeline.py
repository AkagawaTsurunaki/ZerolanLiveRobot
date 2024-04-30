from dataclasses import dataclass
from enum import Enum
import random

from config import GlobalConfig
from common.datacls import Danmaku, PlatformConst


class LiveStreamDanmakuSelectionStrategy(Enum):
    LATEST_LONGEST = 'latest_longest'


@dataclass
class LiveStreamQuery:
    strategy: str


class LiveStreamPipeline:

    def __init__(self, cfg: GlobalConfig):
        self.platform = next(iter(cfg.live_stream.platforms))

    def read_danmaku_latest_longest(self, k: int = 3) -> Danmaku | None:
        if self.platform == PlatformConst.BILIBILI:
            import bilibili.service
            danmaku_list = bilibili.service.all_danmakus()
            return self._select_latest_longest(danmaku_list, k)
        else:
            raise NotImplementedError(f'Platform {self.platform} is not supported.')

    @staticmethod
    def _select_latest_longest(danmaku_list: list[Danmaku], k: int) -> Danmaku:
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
