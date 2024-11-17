import asyncio
import threading
from threading import Thread

from loguru import logger
from websockets import ConnectionClosedError
from websockets.asyncio.server import serve, ServerConnection

from services.game.minecraft.data import KonekoProtocol


class KonekoMinecraftAIAgent:

    def __init__(self, host: str, port: int):
        super().__init__()
        self._host = host
        self._port = port
        self._ws: ServerConnection = None
        self._stop_flag = False

    async def _run(self):
        async def handler(websocket: ServerConnection):
            self._ws = websocket
            while not self._stop_flag:
                msg = await websocket.recv()
                logger.info(msg)

        # set this future to exit the server
        stop = asyncio.get_running_loop().create_future()

        async with serve(handler, self._host, self._port):
            await stop

    def start(self):
        asyncio.run(self._run())

    async def send_message(self, msg: KonekoProtocol):
        msg = msg.to_json()
        if self._ws is None:
            logger.warning("No client connected to your Websocket server. Send message makes no effort.")
            return

        try:
            await self._ws.send(msg)
        except ConnectionClosedError as e:
            logger.error(e)
            logger.warning("KonekoMinecraftBot should send close message to close this connection. Check your bot is still online?")
        except Exception as e:
            logger.exception(e)

    def stop(self):
        self._stop_flag = True
