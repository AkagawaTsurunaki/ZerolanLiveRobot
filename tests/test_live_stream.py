import asyncio

from common.config import get_config
from event.event_data import DanmakuEvent
from event.eventemitter import emitter
from services.live_stream.bilibili import BilibiliService
from services.live_stream.twitch import TwitchService
from services.live_stream.youtube import YouTubeService

_config = get_config()


@emitter.on("service/live-stream/danmaku")
async def handle(event: DanmakuEvent):
    print(event.danmaku.content)


async def async_test_bilibili():
    emitter_task = asyncio.create_task(emitter.start())
    bilibili = BilibiliService(_config.service.live_stream.bilibili)
    bili_task = asyncio.create_task(bilibili.start())
    await asyncio.sleep(3)
    await bilibili.stop()
    await emitter.stop()
    await bili_task
    await emitter_task


def test_bilibili():
    asyncio.run(async_test_bilibili())


def test_twitch():
    twitch = TwitchService(_config.service.live_stream.twitch)
    twitch.start()


def test_youtube():
    youtube = YouTubeService(_config.service.live_stream.youtube)
    youtube.start()
