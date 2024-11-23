from common.config import get_config
from services.live_stream.bilibili import BilibiliService
from services.live_stream.twitch import TwitchService
from services.live_stream.youtube import YouTubeService

config = get_config()


def test_bilibili():
    bilibili = BilibiliService(config.service.live_stream.bilibili)
    bilibili.start()


def test_twitch():
    twitch = TwitchService(config.service.live_stream.twitch)
    twitch.start()


def test_youtube():
    youtube = YouTubeService(config.service.live_stream.youtube)
    youtube.start()
