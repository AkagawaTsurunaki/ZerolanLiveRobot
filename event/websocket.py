import asyncio
import json
from asyncio import Task, TaskGroup
from typing import List

import websockets
from deprecated.sphinx import deprecated
from loguru import logger
from websockets import serve, ConnectionClosedError
from websockets.asyncio.server import ServerConnection
from websockets.protocol import State

from common.abs_runnable import AbstractRunnable
from common.enumerator import EventEnum
from event.event_data import WebSocketJsonReceivedEvent
from event.eventemitter import EventEmitter, emitter


@deprecated(version="2.1")
class OldWebSocketServer(EventEmitter):

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


class WebSocketServer(AbstractRunnable):

    def name(self):
        return "WebSocketServer"

    def __init__(self, host: str, port: int):
        super().__init__()
        self._host = host
        self._port = port
        self._connections: List[ServerConnection] = []
        self._stop_flag = False
        self._server_task: Task = None

    async def start(self):
        """
        异步启动 WebSocket 服务器
        Start the WebSocket server asynchronously
        """
        await super().start()
        try:
            self._server_task = asyncio.create_task(self._run())
        except asyncio.exceptions.CancelledError:
            logger.debug("WebSocket server stopped.")

    def _add_connection(self, websocket: ServerConnection):
        self._connections.append(websocket)
        logger.info(f"WebSocket client connected: {websocket.id}")

    async def _run(self):
        try:
            server = await serve(self._handler, self._host, self._port)
            await server.serve_forever()
        except OSError as e:
            # 端口冲突
            if e.errno == 10048:
                logger.error(
                    "Typically, each socket address (protocol/network address/port) is only allowed to be used once.")
                raise e

    async def _handler(self, websocket: ServerConnection):
        self._add_connection(websocket)
        try:
            while not self._stop_flag:
                msg = await websocket.recv()
                data = json.loads(msg)
                logger.info(f"Web Socket server received: {data}")
                emitter.emit(WebSocketJsonReceivedEvent(data=data))
        except websockets.exceptions.ConnectionClosedOK:
            logger.info("WebSocket client disconnected.")

    async def _send_json(self, ws: ServerConnection, msg: dict | list):
        assert isinstance(msg, dict) or isinstance(msg, list)
        if ws is None or ws.state != State.OPEN:
            logger.warning("No connection.")
            return

        msg = json.dumps(msg, ensure_ascii=False, indent=4)

        try:
            await ws.send(msg)
            logger.info(f"JSON message sent: {msg}")
        except ConnectionClosedError as e:
            logger.exception(e)
            logger.warning("A client disconnected from Web Socket server.")
        except Exception as e:
            logger.exception(e)

    async def send_json(self, msg: dict | list):
        """
        向所有已开放连接的 WebSocket 客户端发送 JSON 信息
        Args:
            msg: 可以被序列化的消息对象
        """
        tasks = []
        async with TaskGroup() as tg:
            if len(self._connections) == 0:
                logger.warning("No WebSocket connection opened. This message will be ignored.")
                return
            for connection in self._connections:
                task = tg.create_task(self._send_json(connection, msg))
                tasks.append(task)

    async def stop(self):
        """
        异步关闭 WebSocket 服务器
        """
        await super().stop()
        self._stop_flag = True
        for connection in self._connections:
            await connection.close(reason="ZerolanLiveRobot shutdown.")
        if self._server_task is not None:
            self._server_task.cancel()
        logger.info("WebSocket server stopped.")
