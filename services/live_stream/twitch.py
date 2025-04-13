"""
Modified from:
    https://pytwitchapi.dev/en/stable/modules/twitchAPI.chat.html#commands
"""

from asyncio import Task

from loguru import logger
from twitchAPI.chat import Chat, EventData, ChatMessage
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope, ChatEvent
from zerolan.data.data.danmaku import Danmaku, SuperChat

from common.concurrent.abs_runnable import AsyncRunnable
from services.live_stream.config import TwitchServiceConfig
from common.decorator import log_start, log_stop
from common.utils.str_util import is_blank
from event.event_data import LiveStreamSuperChatEvent, LiveStreamDanmakuEvent, LiveStreamConnectedEvent, LiveStreamDisconnectedEvent
from event.event_emitter import emitter


class TwitchService(AsyncRunnable):
    def name(self):
        return "TwitchService"

    def __init__(self, config: TwitchServiceConfig):
        """
        TODO: Need test!
        """
        super().__init__()
        assert not is_blank(config.channel_id), f"No channel_id provided."
        assert not is_blank(config.app_id), f"No app_id provided."
        assert not is_blank(config.app_secret), f"No app_secret provided."
        self._target_channel: str = config.channel_id
        self._app_id: str = config.app_id
        self._app_secret: str = config.app_secret
        self._user_scope = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
        self._twitch: Twitch | None = None

        self._service_task: Task | None = None

    @log_start("TwitchService")
    async def start(self):
        await super().start()
        await self.init()

    @log_stop("TwitchService")
    async def stop(self):
        await super().stop()
        await self._twitch.close()

    async def init(self):
        self._twitch = await Twitch(self._app_id, self._app_secret)
        auth = UserAuthenticator(self._twitch, self._user_scope)
        token, refresh_token = await auth.authenticate()
        await self._twitch.set_user_authentication(token, self._user_scope, refresh_token)

        # create chat instance
        chat = await Chat(self._twitch)

        async def on_message(msg: ChatMessage):
            logger.info(f"Danmaku: [{msg.user.name}] {msg.text}")

            if msg.bits is not None and msg.bits > 0:
                sc = SuperChat(uid=msg.user.id, username=msg.user.name, content=msg.text, ts=msg.sent_timestamp,
                               money=f'{msg.bits}')
                emitter.emit(LiveStreamSuperChatEvent(superchat=sc, platform="twitch"))
            else:
                danmaku = Danmaku(uid=msg.user.id, username=msg.user.name, content=msg.text, ts=msg.sent_timestamp)
                emitter.emit(LiveStreamDanmakuEvent(danmaku=danmaku, platform="twitch"))

        async def on_ready(ready_event: EventData):
            await ready_event.chat.join_room(self._target_channel)
            if ready_event.chat.is_connected():
                emitter.emit(LiveStreamConnectedEvent(platform="twitch"))
                logger.info(f"Joined channel: {self._target_channel}")
            else:
                emitter.emit(LiveStreamDisconnectedEvent(platform="twitch", reason="未成功连接"))
                logger.error(f"Failed to join channel: {self._target_channel}")

        chat.register_event(ChatEvent.READY, on_ready)
        chat.register_event(ChatEvent.MESSAGE, on_message)
