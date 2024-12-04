from asyncio import TaskGroup
from typing import List, TypeVar

from loguru import logger

from common.abs_runnable import AbstractRunnable
from common.config import LiveStreamConfig
from common.decorator import log_start, log_stop
from services.live_stream.bilibili import BilibiliService
from services.live_stream.twitch import TwitchService
from services.live_stream.youtube import YouTubeService

T = TypeVar(name='T', bound=AbstractRunnable)


class LiveStreamService(AbstractRunnable):

    def name(self):
        return "LiveStreamService"

    def __init__(self, config: LiveStreamConfig):
        super().__init__()
        self._enable: bool = config.enable
        self._platforms: List[T] = []
        errs = []
        if self._enable:
            platforms = {
                BilibiliService: config.bilibili,
                TwitchService: config.twitch,
                YouTubeService: config.youtube,
            }

            for service, cfg in platforms.items():
                try:
                    platform = service(cfg)
                    self._platforms.append(platform)
                except Exception as e:
                    errs.append(e)

            if len(errs) == len(platforms):
                logger.error(
                    "You have enabled `live_stream`, but none of the platforms have been successfully connected.")
                raise RuntimeError("Failed to connect any live streaming platform.")

    @log_start("LiveStreamService")
    async def start(self):
        if self._enable:
            async with TaskGroup() as tg:
                tasks = []
                logger.info(f"Start live stream platform: {len(self._platforms)}")
                for platform in self._platforms:
                    task = tg.create_task(platform.start())
                    tasks.append(task)

    @log_stop("LiveStreamService")
    async def stop(self):
        if self._enable:
            for platform in self._platforms:
                await platform.stop()
