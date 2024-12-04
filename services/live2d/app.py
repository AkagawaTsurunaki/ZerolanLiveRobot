import os
from asyncio import TaskGroup
from os.path import abspath
from typing import Optional

from loguru import logger
from pydantic import BaseModel, Field, ValidationError

from common.abs_runnable import AbstractRunnable
from common.config import Live2DConfig
from common.decorator import log_start, log_stop
from common.enumerator import EventEnum
from event.event_data import WebSocketJsonReceivedEvent
from event.websocket import WebSocketServer


class ZerolanLive2DProtocol(BaseModel):
    Protocol: str = "Zerolan Live2D Protocol"
    Version: str = "0.1"
    Event: str = Field(default=None)
    Data: Optional[any] = Field(default=None)


class Live2dApplication(AbstractRunnable):
    def name(self):
        return "Live2dApplication"

    def __init__(self, config: Live2DConfig):
        super().__init__()
        self._model_dir = abspath(config.model_dir)
        assert os.path.exists(self._model_dir), f"{self._model_dir} does not exist."
        self._ws = WebSocketServer(config.host, config.port)

    @log_start("Live2dApplication")
    async def start(self):
        await super().start()
        async with TaskGroup() as tg:
            self.init()
            tg.create_task(self._ws.start())

    @log_stop("Live2dApplication")
    async def stop(self):
        await super().stop()
        await self._ws.stop()

    def validate_protocol(self, data: any) -> ZerolanLive2DProtocol | None:
        try:
            recv_obj = ZerolanLive2DProtocol.model_validate(data)
            if recv_obj.Protocol == "Zerolan Live2D Protocol" and recv_obj.Version == "0.1":
                return recv_obj
        except ValidationError as e:
            pass
        return None

    def init(self):
        @self._ws.on(EventEnum.WEBSOCKET_RECV_JSON)
        async def on(event: WebSocketJsonReceivedEvent):
            protocol = self.validate_protocol(event.data)
            if protocol is None:
                return
            logger.debug(protocol)
            if protocol.Event == "client_hello":
                logger.info("Client Hello")

                obj = ZerolanLive2DProtocol()
                obj.Event = "load_live2d_model"

                obj.Data = {
                    "ModelDirectory": self._model_dir
                }
                await self._ws.send_json(obj.model_dump())
