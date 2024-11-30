"""
Modified from:
    https://pytwitchapi.dev/en/stable/modules/twitchAPI.chat.html#commands
"""

import asyncio

from loguru import logger
from twitchAPI.chat import Chat, EventData, ChatMessage
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope, ChatEvent
from zerolan.data.data.danmaku import Danmaku, SuperChat

from common.config import TwitchServiceConfig
from common.decorator import log_start, log_stop
from common.enumerator import EventEnum
from common.utils.str_util import is_blank
from event.eventemitter import emitter


class TwitchService:
    def __init__(self, config: TwitchServiceConfig):
        """
        TODO: Need test!
        """
        assert not is_blank(config.channel_id), f"No channel_id provided."
        assert not is_blank(config.app_id), f"No app_id provided."
        assert not is_blank(config.app_secret), f"No app_secret provided."
        self._target_channel: str = config.channel_id
        self._app_id: str = config.app_id
        self._app_secret: str = config.app_secret
        self._user_scope = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

    @log_start("TwitchService")
    def start(self):
        asyncio.run(self.init())

    @log_stop("TwitchService")
    def stop(self):
        close_task = asyncio.create_task(self.twitch.close())
        asyncio.gather(close_task)

    async def init(self):
        self.twitch = await Twitch(self._app_id, self._app_secret)
        auth = UserAuthenticator(self.twitch, self._user_scope)
        token, refresh_token = await auth.authenticate()
        await self.twitch.set_user_authentication(token, self._user_scope, refresh_token)

        # create chat instance
        chat = await Chat(self.twitch)

        async def on_message(msg: ChatMessage):
            logger.info(f"Danmaku: [{msg.user.name}] {msg.text}")

            if msg.bits is not None and msg.bits > 0:
                sc = SuperChat(uid=msg.user.id, username=msg.user.name, content=msg.text, ts=msg.sent_timestamp,
                               money=f'{msg.bits}')
                emitter.emit(EventEnum.SERVICE_LIVE_STREAM_SUPER_CHAT, sc)
            else:
                danmaku = Danmaku(uid=msg.user.id, username=msg.user.name, content=msg.text, ts=msg.sent_timestamp)
                emitter.emit(EventEnum.SERVICE_LIVE_STREAM_DANMAKU, danmaku)

        async def on_ready(ready_event: EventData):
            await ready_event.chat.join_room(self._target_channel)
            if ready_event.chat.is_connected():
                emitter.emit(EventEnum.SERVICE_LIVE_STREAM_CONNECTED)
                logger.info(f"Joined channel: {self._target_channel}")
            else:
                emitter.emit(EventEnum.SERVICE_LIVE_STREAM_DISCONNECTED)
                logger.error(f"Failed to join channel: {self._target_channel}")

        chat.register_event(ChatEvent.READY, on_ready)
        chat.register_event(ChatEvent.MESSAGE, on_message)
