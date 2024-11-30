import asyncio
import json

import websockets
from loguru import logger
from websockets import serve, ConnectionClosedError
from websockets.asyncio.server import ServerConnection

from common.enumerator import EventEnum
from event.eventemitter import EventEmitter


class WebSocketServer(EventEmitter):

    def __init__(self, host: str, port: int):
        super().__init__()
        self._host = host
        self._port = port
        self._ws: ServerConnection
        self._stop_flag = False

    def start(self):
        asyncio.run(self._run())

    async def _run(self):
        try:
            server = await serve(self._handler, self._host, self._port)
            serve_coro = server.serve_forever()
            loop = asyncio.get_event_loop()
            self._task = loop.create_task(serve_coro)
            await asyncio.gather(self._task)
        except OSError as e:
            if e.errno == 10048:
                logger.error(
                    "Typically, each socket address (protocol/network address/port) is only allowed to be used once.")
                raise e
        except asyncio.exceptions.CancelledError:
            logger.debug("WebSocket exited from the running loop.")

    async def _handler(self, websocket: ServerConnection):
        self._ws = websocket
        logger.info(f"WebSocket client connected.")
        try:
            while not self._stop_flag:
                msg = await websocket.recv()
                data = json.loads(msg)
                await self.emit(EventEnum.WEBSOCKET_RECV_JSON, data)
                logger.info(f"Web Socket server received: {data}")
        except websockets.exceptions.ConnectionClosedOK:
            logger.info("WebSocket client disconnected.")


    async def send_json(self, msg: dict | list):
        assert isinstance(msg, dict) or isinstance(msg, list)
        try:
            msg = json.dumps(msg, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.exception(e)
            return
        if self._ws is None:
            logger.warning("No client connected to your Websocket server. Send message makes no effort.")
            return
        try:
            await self._ws.send(msg)
            logger.info(f"Send: {msg}")
        except ConnectionClosedError as e:
            logger.exception(e)
            logger.warning("A client disconnected from Web Socket server.")
        except Exception as e:
            logger.exception(e)

    def stop(self):
        super().stop()
        self._stop_flag = True
        # loop = asyncio.get_event_loop()
        self._task.cancel()

        logger.info("WebSocket server stopped.")
