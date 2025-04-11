from asyncio import TaskGroup

from bilibili_api import Credential
from bilibili_api.live import LiveDanmaku
from loguru import logger
from zerolan.data.data.danmaku import Danmaku

from common.concurrent.abs_runnable import AbstractRunnable
from common.decorator import log_init, log_stop
from event.event_data import LiveStreamConnectedEvent, DanmakuEvent, LiveStreamDisconnectedEvent, GiftEvent
from event.event_emitter import emitter
from services.live_stream.config import BilibiliServiceConfig
from services.live_stream.data import Gift


class BilibiliService(AbstractRunnable):

    def name(self):
        return "BilibiliService"

    @log_init("BilibiliService")
    def __init__(self, config: BilibiliServiceConfig):
        super().__init__()
        assert config.room_id and config.room_id > 0, "Room id must be greater than 0"
        self._room_id: int = config.room_id
        self._retry_count = 0
        self._max_retry = 5

        credential = Credential(sessdata=config.credential.sessdata,
                                bili_jct=config.credential.bili_jct,
                                buvid3=config.credential.buvid3)
        self._monitor = LiveDanmaku(self._room_id, credential=credential, retry_after=3, max_retry=self._max_retry)
        self._init()

    async def start(self):
        logger.info(f"{self.name()} start.")
        tasks = []
        async with TaskGroup() as tg:
            tasks.append(tg.create_task(super().start()))
            tasks.append(tg.create_task(self._monitor.connect()))
        logger.info(f"{self.name()} exited.")

    def _init(self):
        """
        See: https://nemo2011.github.io/bilibili-api/#/modules/live
        :return:
        """

        @self._monitor.on("VERIFICATION_SUCCESSFUL")
        def on_connect(_):
            logger.info("Verification successful, connected to Bilibili server.")
            emitter.emit(LiveStreamConnectedEvent(platform="bilibili"))

        @self._monitor.on('DANMU_MSG')
        def on_danmaku(event):
            uid = str(event["data"]["info"][2][0])
            username = event["data"]["info"][2][1]
            content = event["data"]["info"][1]
            ts = event["data"]["info"][9]['ts']
            danmaku = Danmaku(uid=uid, username=username, content=content, ts=ts)
            # 注意没带粉丝牌的会导致越界
            # fans_band_level = event["data"]["info"][3][0]  # 粉丝牌的级别
            # fans_band_name = event["data"]["info"][3][1]  # 该粉丝牌的名字
            # live_host_name = event["data"]["info"][3][2]  # 该粉丝牌对应的主播名字
            logger.info(f"Danmaku: [{danmaku.username}] {danmaku.content}")
            emitter.emit(DanmakuEvent(platform="bilibili", danmaku=danmaku))

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
            emitter.emit(LiveStreamDisconnectedEvent(platform="bilibili", reason="Disconnected from Bilibili server."))
            logger.info("Disconnected from Bilibili server.")

        @self._monitor.on("SEND_GIFT")
        def handle_send_gift(event):
            info = event['data']['data']
            uid, gift_name, num, username = info['uid'], info['giftName'], info['num'], info['uname']
            gift = Gift(uid=uid, gift_name=gift_name, num=num, username=username)
            emitter.emit(GiftEvent(gift=gift, platform="bilibili"))

        @self._monitor.on("SUPER_CHAT_MESSAGE")
        async def handle_super_chat_message(event):
            # TODO: Need to parse event
            # emitter.emit("service.live_stream.super_chat")
            logger.debug(event)
            pass

    @log_stop("BilibiliService")
    async def stop(self):
        await super().stop()
        await self._monitor.disconnect()
