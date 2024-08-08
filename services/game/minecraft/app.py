from flask import Flask, request
from loguru import logger

from common.buffer.game_buf import MinecraftGameEvent, MinecraftGameEventBuffer
from common.config.service_config import ServiceConfig

config = ServiceConfig.game_config


class MinecraftEventListeningApplication:

    def __init__(self):
        super().__init__()
        self._app = Flask(__name__)
        self._app.add_url_rule(rule='/game/minecraft', view_func=self._handle_add_game_event,
                               methods=["GET", "POST"])
        self.game_evt_buf: MinecraftGameEventBuffer = MinecraftGameEventBuffer()

    def start(self):
        self._app.run(host=config.host, port=config.port, debug=False)

    def _handle_add_game_event(self):
        with self._app.app_context():
            try:
                game_event: MinecraftGameEvent = MinecraftGameEvent.from_json(request.json)  # type: ignore
                if game_event:
                    self.game_evt_buf.append(game_event)
                    logger.info(f'Game Event: {game_event}')
                    return 'OK.', 200
            except Exception as e:
                logger.exception(e)
                return "Failed to add event.", 500
