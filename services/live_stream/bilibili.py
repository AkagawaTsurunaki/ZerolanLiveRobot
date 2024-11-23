from bilibili_api import Credential, sync
from bilibili_api.live import LiveDanmaku
from loguru import logger
from zerolan.data.data.danmaku import Danmaku

from common.config import BilibiliServiceConfig
from common.decorator import log_init, log_start, log_stop
from common.enumerator import EventEnum
from event.eventemitter import emitter


class BilibiliService:

    @log_init("BilibiliService")
    def __init__(self, config: BilibiliServiceConfig):
        assert config.room_id and config.room_id > 0, "Room id must be greater than 0"
        self._room_id: int = config.room_id
        self._retry_count = 0
        self._max_retry = 5

        credential = Credential(sessdata=config.credential.sessdata,
                                bili_jct=config.credential.bili_jct,
                                buvid3=config.credential.buvid3)
        self._monitor = LiveDanmaku(self._room_id, credential=credential, retry_after=3, max_retry=self._max_retry)
        self.register_listeners()

    @log_start("BilibiliService")
    def start(self):
        sync(self._monitor.connect())

    def register_listeners(self):
        """
        See: https://nemo2011.github.io/bilibili-api/#/modules/live
        :return:
        """

        @self._monitor.on("VERIFICATION_SUCCESSFUL")
        async def on_connect(event):
            emitter.emit(EventEnum.SERVICE_LIVE_STREAM_CONNECTED)
            logger.info("Verification successful, connected to Bilibili server.")

        @self._monitor.on("DANMU_MSG")
        async def handle_recv(event):
            danmaku = Danmaku(uid=event["data"]["info"][2][0],
                              username=event["data"]["info"][2][1],
                              content=event["data"]["info"][1],
                              ts=event["data"]["info"][9]['ts'])
            # 注意没带粉丝牌的会导致越界
            # fans_band_level = event["data"]["info"][3][0]  # 粉丝牌的级别
            # fans_band_name = event["data"]["info"][3][1]  # 该粉丝牌的名字
            # live_host_name = event["data"]["info"][3][2]  # 该粉丝牌对应的主播名字
            logger.info(f"Danmaku: [{danmaku.username}] {danmaku.msg}")
            await emitter.emit(EventEnum.SERVICE_LIVE_STREAM_DANMAKU, danmaku=danmaku)

        @self._monitor.on("DISCONNECT")
        async def handle_disconnect():
            self._retry_count += 1
            if self._retry_count >= self._max_retry:
                logger.warning("""
                An error occurred during the connection to the Bilibili server, you can try:
                1. Check your Internet connection.
                2. Check your credential information in `config.yaml`.
                3. Update the `bilibili-api-python` package to the latest version.
                """)
            emitter.emit(EventEnum.SERVICE_LIVE_STREAM_DISCONNECTED)
            logger.info("Disconnected from Bilibili server.")

        @self._monitor.on("SEND_GIFT")
        async def handle_send_gift(event):
            # TODO: Need to parse event
            # emitter.emit("service.live_stream.gift")
            logger.debug(event)
            pass

        @self._monitor.on("SUPER_CHAT_MESSAGE")
        async def handle_super_chat_message(event):
            # TODO: Need to parse event
            # emitter.emit("service.live_stream.super_chat")
            logger.debug(event)
            pass

    @log_stop("BilibiliService")
    def stop(self):
        sync(self._monitor.disconnect())
