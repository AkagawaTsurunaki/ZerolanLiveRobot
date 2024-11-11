from bilibili_api import Credential, sync
from bilibili_api.live import LiveDanmaku
from loguru import logger

from common.buffer.danmaku_buffer import DanmakuBuffer, DanmakuBufferObject
from common.config.service_config import ServiceConfig
from zerolan.data.data.danmaku import Danmaku

config = ServiceConfig.live_stream_config
assert config.platform == "bilibili", f"当前配置中指定的直播间平台是 {config.platform} 而不是 bilibili"


class BilibiliService:
    def __init__(self):
        self._room_id: int = int(config.room_id)
        credential = Credential(sessdata=config.credential.sessdata,
                                bili_jct=config.credential.bili_jct,
                                buvid3=config.credential.buvid3)
        self._monitor = LiveDanmaku(self._room_id, credential=credential, retry_after=2, max_retry=5)
        self.danmaku_buf: DanmakuBuffer = DanmakuBuffer()
        logger.info("初始化完成")

    def start(self):
        logger.info(f'开始监听直播间')

        @self._monitor.on("DANMU_MSG")
        async def recv(event):
            danmaku = Danmaku(uid=event["data"]["info"][2][0],
                              username=event["data"]["info"][2][1],
                              msg=event["data"]["info"][1],
                              ts=event["data"]["info"][9]['ts'])
            # 注意没带粉丝牌的会导致越界
            # fans_band_level = event["data"]["info"][3][0]  # 粉丝牌的级别
            # fans_band_name = event["data"]["info"][3][1]  # 该粉丝牌的名字
            # live_host_name = event["data"]["info"][3][2]  # 该粉丝牌对应的主播名字

            self.danmaku_buf.append(DanmakuBufferObject(danmaku))
            logger.info(f'获取弹幕（{len(self.danmaku_buf.select_all_unprocessed())}/{len(self.danmaku_buf)}）：{danmaku}')

        sync(self._monitor.connect())
        if self._monitor.get_status() == LiveDanmaku.STATUS_ERROR:
            logger.error("与 Bilibili 服务器的连接过程中发生了错误，您可以尝试：\n1. 更新配置文件中的身份信息。\n2. 更新 bilibili-api-python 包至最新版本。")
        logger.warning(f'断开了与直播间的连接')
