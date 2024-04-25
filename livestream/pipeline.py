from utils.datacls import Danmaku, Platform
from config import GLOBAL_CONFIG as G_CFG


class LiveStreamPipeline:

    def __init__(self):
        self.platform = next(iter(G_CFG.live_stream.platforms))

    def read_danmaku_latest_longest(self, k: int = 3) -> Danmaku | None:
        if self.platform == Platform.BILIBILI:
            import bilibili.service
            return bilibili.service.select_latest_longest(k)
        else:
            raise NotImplementedError(f'Platform {self.platform} is not supported.')
