import asyncio

import requests
from pydantic import BaseModel
from zerolan.data.data.danmaku import Danmaku

from common.config import YoutubeServiceConfig
from common.decorator import log_start, log_stop
from common.enumerator import EventEnum
from event.eventemitter import emitter


class SuperChat(BaseModel):
    uid: str
    username: str
    ts: float
    content: str
    money: str


def get(url, token: str):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def convert_danmakus(live_chat_messages: list[dict]):
    result = []
    for live_chat_message in live_chat_messages:
        if live_chat_message["type"] == "textMessageEvent":
            ts = live_chat_message["snippet"]["publishedAt"]
            content = live_chat_message["snippet"]["textMessageDetails"]["messageText"]
            uid = live_chat_message["snippet"]["authorDetails"]["channelId"]
            username = live_chat_message["snippet"]["authorDetails"]["displayName"]
            danmaku = Danmaku(uid=uid, username=username, msg=content, ts=ts)
            result.append(danmaku)
    return result


def convert_superchats(super_chat_events: list[dict]):
    result = []
    for super_chat_event in super_chat_events:
        uid = super_chat_event["snippet"]["channelId"]
        username = super_chat_event["snippet"]["displayName"]
        ts = super_chat_event["snippet"]["createdAt"]
        content = super_chat_event["snippet"]["commentText"]
        money = super_chat_event["snippet"]["displayString"]
        sc = SuperChat(uid=uid, username=username, ts=ts, content=content, money=money)
        result.append(sc)
    return result


class YouTubeService:
    def __init__(self, config: YoutubeServiceConfig):
        assert config.token is not None or config.token == "", f"No token provided."
        self._token = config.token
        self._danmakus = set()
        self._superchats = set()
        self._stop_flag = False

    async def _run(self):
        while not self._stop_flag:
            await asyncio.sleep(1)
            self.emit_danmaku_event()
            self.emit_super_chat_event()

    def emit_danmaku_event(self):
        # https://developers.google.com/youtube/v3/live/docs/liveChatMessages
        live_chat_messages = get("https://www.googleapis.com/youtube/v3/liveChat/messages", self._token)
        danmakus = set(convert_danmakus(live_chat_messages["items"]))
        updated_danmakus = self._danmakus.difference(danmakus)
        self._danmakus.update(updated_danmakus)
        for danmaku in updated_danmakus:
            emitter.emit(EventEnum.SERVICE_LIVE_STREAM_DANMAKU, danmaku)

    def emit_super_chat_event(self):
        # https://developers.google.com/youtube/v3/live/docs/superChatEvents
        super_chat_events = get("https://www.googleapis.com/youtube/v3/superChatEvents", self._token)
        super_chats = convert_superchats(super_chat_events["items"])
        updated_superchats = self._superchats.difference(super_chats)
        self._superchats.update(updated_superchats)
        for superchat in updated_superchats:
            emitter.emit(EventEnum.SERVICE_LIVE_STREAM_SUPER_CHAT, superchat)

    @log_start("YouTubeService")
    def start(self):
        asyncio.run(self._run())

    @log_stop("YouTubeService")
    def stop(self):
        self._stop_flag = True
