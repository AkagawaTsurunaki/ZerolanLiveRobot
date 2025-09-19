from ncatbot.core import BaseMessageEvent, BotClient
from loguru import logger
from services.qqbot.config import QQBotServiceConfig
from ncatbot.plugin_system import command_registry


class QQBotService:
    def __init__(self, config: QQBotServiceConfig):
        self._bot = BotClient()
        self._api = self._bot.run_backend(bt_uin=config.qq_num, ws_uri=config.ws_uri,
                                          ws_token=config.ws_token, debug=False)
        self._root_user = config.root
        logger.info("QQ bot!")

        @command_registry.command("hello")
        async def hello_cmd(self, event: BaseMessageEvent):
            await event.reply("hello")

    def start(self):
        self._api.send_private_text_sync(self._root_user, "hello")

    def stop(self):
        pass
