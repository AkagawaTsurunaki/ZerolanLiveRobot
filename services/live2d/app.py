import os
from os.path import abspath

from loguru import logger
from zerolan.data.protocol.protocol import ZerolanProtocol

from common.config import Live2DConfig
from event.event_data import WebSocketJsonReceivedEvent
from event.websocket import WebSocketServer, ZerolanProtocolWebsocket


class Live2dApplication(ZerolanProtocolWebsocket):
    def name(self):
        return "Live2dApplication"

    def __init__(self, config: Live2DConfig):
        super().__init__(config.host, config.port)
        self._model_dir = abspath(config.model_dir)
        assert os.path.exists(self._model_dir), f"{self._model_dir} does not exist."
        self._ws = WebSocketServer(config.host, config.port)

    @property
    def is_connected(self):
        if self._ws.connections > 0:
            return True
        return False

    def init(self):
        @self._ws.on("websocket/json-received")
        async def on(event: WebSocketJsonReceivedEvent):
            protocol = self.validate_protocol(event.data)
            if protocol is None:
                return
            logger.debug(protocol)
            if protocol.Event == "client_hello":
                logger.info("Client Hello")

                obj = ZerolanProtocol()
                obj.Event = "load_live2d_model"

                obj.Data = {
                    "ModelDirectory": self._model_dir
                }
                await self._ws.send_json(obj.model_dump())

    async def playsound(self, filepath: str, text: str = ""):
        raise NotImplemented("Deprecated")
