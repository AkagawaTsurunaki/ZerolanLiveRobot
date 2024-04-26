from config import GlobalConfig
from utils.datacls import Danmaku, PlatformConst


class LiveStreamPipeline:

    def __init__(self, cfg: GlobalConfig):
        self.platform = next(iter(cfg.live_stream.platforms))

    def read_danmaku_latest_longest(self, k: int = 3) -> Danmaku | None:
        if self.platform == PlatformConst.BILIBILI:
            import bilibili.service
            return bilibili.service.select_latest_longest(k)
        else:
            raise NotImplementedError(f'Platform {self.platform} is not supported.')
