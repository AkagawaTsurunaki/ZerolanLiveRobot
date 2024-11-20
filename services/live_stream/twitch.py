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
from zerolan.data.data.danmaku import Danmaku

from common.decorator import log_start
from common.enumerator import EventEnum
from event.eventemitter import emitter


class TwitchService:
    def __init__(self):
        """
        TODO: This class is not under testing yet
        """
        self._app_id: str = ""
        self._app_secret: str = ""
        self._user_scope = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
        self._target_channel: str = ""

    @log_start("TwitchService")
    def start(self):
        asyncio.run(self.init())

    async def init(self):
        twitch = await Twitch(self._app_id, self._app_secret)
        auth = UserAuthenticator(twitch, self._user_scope)
        token, refresh_token = await auth.authenticate()
        await twitch.set_user_authentication(token, self._user_scope, refresh_token)

        # create chat instance
        chat = await Chat(twitch)

        async def on_message(msg: ChatMessage):
            logger.info(f"Danmaku: [{msg.user.name}] {msg.text}")
            danmaku = Danmaku(uid=msg.user.id, username=msg.user.name, msg=msg.text, ts=msg.sent_timestamp)
            if msg.bits is not None and msg.bits > 0:
                # TODO: add bits amount into instance of Danmaku
                emitter.emit(EventEnum.SERVICE_LIVE_STREAM_SUPER_CHAT, danmaku)
            else:
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
