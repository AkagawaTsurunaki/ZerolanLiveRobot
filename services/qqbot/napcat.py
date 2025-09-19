import os
import time
from ncatbot.core import BotClient, GroupMessageEvent
from loguru import logger
from typeguard import typechecked
from bot import QQMessageEvent, emitter
from services.qqbot.config import QQBotServiceConfig
from ncatbot.plugin_system import command_registry


class QQBotService:
    def __init__(self, config: QQBotServiceConfig):
        self._bot = BotClient()
        self._api = self._bot.run_backend(bt_uin=config.qq_num, ws_uri=config.ws_uri,
                                          ws_token=config.ws_token, debug=False)
        self._root_user = config.root
        logger.info("QQ bot!")
        self._last_sent_time = time.time()

        @self._bot.on_group_message
        async def echo_cmd(event: GroupMessageEvent):
            text = "".join(seg.text for seg in event.message.filter_text())
            if "echo" in text:
                if self.can_send():
                    await event.reply(text[4:])
                    self.set_timer()

        @self._bot.on_group_message
        async def emit_plain_text_msg(event: GroupMessageEvent):
            text = "".join(seg.text for seg in event.message.filter_text())
            logger.debug(f"Received QQ message: {text}")
            if self.can_send():
                emitter.emit(QQMessageEvent(
                    message=text, group_id=int(event.group_id)))
                self.set_timer()

    def set_timer(self):
        self._last_sent_time = time.time()

    def can_send(self):
        now = time.time()
        print(now - self._last_sent_time)
        if now - self._last_sent_time > 5:
            return True
        logger.warning("Limit sending QQ message.")
        return False

    @typechecked
    def send_plain_message(self, group_id: int, text: str):
        self._api.send_group_text_sync(group_id, text)
        logger.info(f"Sent QQ message: {text}")

    @typechecked
    def send_speech(self, group_id: int, audio_path: str):
        assert os.path.exists(audio_path)
        self._api.send_group_record_sync(group_id, audio_path)

    def start(self):
        # self._api.send_private_text_sync(self._root_user, "hello")
        pass

    def stop(self):
        pass
