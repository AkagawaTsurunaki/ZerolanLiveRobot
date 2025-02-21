import asyncio
import json
from abc import abstractmethod
from asyncio import Task, TaskGroup
from typing import List

import websockets
from loguru import logger
from pydantic import ValidationError
from websockets import serve, ConnectionClosedError, Subprotocol
from websockets.asyncio.server import ServerConnection
from websockets.protocol import State
from zerolan.data.protocol.protocol import ZerolanProtocol

from common.abs_runnable import AbstractRunnable
from event.event_data import WebSocketJsonReceivedEvent, WebSocketDisconnectedEvent
from event.eventemitter import TypedEventEmitter
from event.registry import EventKeyRegistry


class WebSocketServer(TypedEventEmitter):

    def name(self):
        return "WebSocketServer"

    def __init__(self, host: str, port: int, match_sub_protocol: str | None = None):
        super().__init__()
        self._host = host
        self._port = port
        self._connections: List[ServerConnection] = []
        self._stop_flag = False
        self._server_task: Task = None
        self._match_sub_protocol = match_sub_protocol
        self._error_handlers = []

    async def start(self):
        """
        异步启动 WebSocket 服务器
        Start the WebSocket server asynchronously
        """
        try:
            async with TaskGroup() as tg:
                tg.create_task(super().start())
                tg.create_task(self._run())
                logger.info(f"Start WebSocket server at {self._host}:{self._port}")
        except asyncio.exceptions.CancelledError:
            logger.debug("WebSocket server stopped.")

    def _add_connection(self, websocket: ServerConnection):
        self._connections.append(websocket)
        logger.info(f"WebSocket client connected: {websocket.id}")

    async def _run(self):
        try:
            server = await serve(self._handler, self._host, self._port, subprotocols=[Subprotocol("ZerolanProtocol")])
            await server.serve_forever()
        except OSError as e:
            # 端口冲突
            if e.errno == 10048:
                logger.error(
                    "Typically, each socket address (protocol/network address/port) is only allowed to be used once.")
                raise e

    async def _handler(self, websocket: ServerConnection):
        if self._match_sub_protocol is not None:
            if self._match_sub_protocol != "ZerolanProtocol":
                logger.warning("Not supported sub protocol.")
                return

        self._add_connection(websocket)
        try:
            while not self._stop_flag:
                try:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    logger.info(f"Web Socket server received: {data}")
                    self.emit(WebSocketJsonReceivedEvent(data=data))
                except websockets.exceptions.ConnectionClosedError as e:
                    self._connections.remove(websocket)
                    self.emit(WebSocketDisconnectedEvent())
                    logger.warning("A client disconnected abnormally from the server.")
                    return

        except websockets.exceptions.ConnectionClosedOK:
            self._connections.remove(websocket)
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

    @property
    def connections(self) -> int:
        return len(self._connections)


class ZerolanProtocolWebsocket(AbstractRunnable):

    async def start(self):
        await super().start()
        async with TaskGroup() as tg:
            self.init()
            tg.create_task(self._ws.start())

    async def stop(self):
        await super().stop()
        await self._ws.stop()

    def __init__(self, host: str, port: int):
        super().__init__()
        self._ws = WebSocketServer(host, port, match_sub_protocol="ZerolanProtocol")
        self._protocol = "ZerolanProtocol"
        self._version = "1.1"

    @property
    def is_connected(self):
        if self._ws.connections > 0:
            return True
        return False

    def validate_protocol(self, data: any) -> ZerolanProtocol | None:
        try:
            recv_obj = ZerolanProtocol.model_validate(data)
            if recv_obj.protocol == self._protocol and recv_obj.version == self._version:
                return recv_obj
            else:
                logger.warning("Validation failed.")
        except ValidationError as e:
            logger.warning(e)
            pass
        return None

    def init(self):
        @self._ws.on(EventKeyRegistry._Inner.WEBSOCKET_RECV_JSON)
        async def on(event: WebSocketJsonReceivedEvent):
            protocol = self.validate_protocol(event.data)
            if protocol is None:
                return
            await self.on_protocol(protocol)

    @abstractmethod
    async def on_protocol(self, protocol: ZerolanProtocol):
        raise NotImplementedError()

    async def send(self, action: str, data: any, message: str = "", code: int = 0):
        protocol = ZerolanProtocol(message=message,
                                   code=code,
                                   action=action,
                                   data=data)
        await self._ws.send_json(protocol.model_dump())
