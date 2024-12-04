import threading
from typing import List, TypeVar

from loguru import logger

from common.abs_runnable import AbstractRunnable
from common.config import LiveStreamConfig
from common.decorator import log_start, log_stop
from manager.thread_manager import ThreadManager
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
            self._thread_manager = ThreadManager()
            try:
                bilibili = BilibiliService(config.bilibili)
                self._platforms.append(bilibili)
                self._thread_manager.add_thread(threading.Thread(target=bilibili.start, name="BilibiliService"))
            except Exception as e:
                errs.append(e)
            try:
                twitch = TwitchService(config.twitch)
                self._platforms.append(twitch)
                self._thread_manager.add_thread(threading.Thread(target=twitch.start, name="TwitchService"))
            except Exception as e:
                errs.append(e)
            try:
                youtube = YouTubeService(config.youtube)
                self._platforms.append(youtube)
                self._thread_manager.add_thread(threading.Thread(target=youtube.start, name="YoutubeService"))
            except Exception as e:
                errs.append(e)

            if len(errs) == 3:
                logger.error(
                    "You have enabled `live_stream`, but none of the platforms have been successfully connected.")
                raise RuntimeError("Failed to connect any live streaming platform.")

    @log_start("LiveStreamService")
    async def start(self):
        if self._enable:
            self._thread_manager.start_all()
        self._thread_manager.join_all_threads()

    @log_stop("LiveStreamService")
    async def stop(self):
        if self._enable:
            for serv in self._platforms:
                if hasattr(serv, "stop"):
                    await serv.stop()
