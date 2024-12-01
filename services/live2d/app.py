import os
from os.path import abspath
from typing import Optional

from loguru import logger
from pydantic import BaseModel, Field

from common.config import Live2DConfig
from common.enumerator import EventEnum
from event.websocket import OldWebSocketServer


class ZerolanLive2DProtocol(BaseModel):
    Protocol: str = "Zerolan Live2D Protocol"
    Version: str = "0.1"
    Event: str = Field(default=None)
    Data: Optional[any] = Field(default=None)


class Live2dApplication:
    def __init__(self, config: Live2DConfig):
        self._model_dir = abspath(config.model_dir)
        assert os.path.exists(self._model_dir), f"{self._model_dir} does not exist."
        self._ws = OldWebSocketServer(config.host, config.port)

    def start(self):
        self.init()
        self._ws.start()

    def stop(self):
        self._ws.stop()

    def init(self):
        @self._ws.on(EventEnum.WEBSOCKET_RECV_JSON)
        async def on(data: any):
            recv_obj = ZerolanLive2DProtocol.model_validate(data)
            logger.debug(recv_obj)
            if recv_obj is None:
                return
            if recv_obj.Event == "client_hello":
                logger.info("Client Hello")

                obj = ZerolanLive2DProtocol()
                obj.Event = "load_live2d_model"

                obj.Data = {
                    "ModelDirectory": self._model_dir
                }
                await self._ws.send_json(obj.model_dump())
