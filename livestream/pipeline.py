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
        self.platform = cfg.live_stream.platforms[0].platform_name

    def read_danmaku_latest_longest(self, k: int = 3) -> Danmaku | None:
        if self.platform == PlatformConst.BILIBILI:
            import livestream.bilibili.service
            return livestream.bilibili.service.select_latest_longest(k=3)
        else:
            raise NotImplementedError(f'Platform {self.platform} is not supported.')


