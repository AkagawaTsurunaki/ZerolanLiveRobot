import asyncio
import threading
from threading import Thread

from loguru import logger
from websockets.asyncio.server import serve, ServerConnection

from common.buffer.game_buf import MinecraftGameEventBuffer
from services.game.minecraft.data import KonekoProtocol


class KonekoMinecraftAIAgent:

    def __init__(self, host: str, port: int):
        super().__init__()
        self.game_evt_buf: MinecraftGameEventBuffer = MinecraftGameEventBuffer()
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

    def start(self) -> Thread:
        def asyncio_run():
            asyncio.run(self._run())

        t = threading.Thread(target=asyncio_run, daemon=True)
        t.start()
        return t

    async def send_message(self, msg: KonekoProtocol):
        msg = msg.to_json()
        if self._ws is not None:
            await self._ws.send(msg)

    def stop(self):
        self._stop_flag = True
