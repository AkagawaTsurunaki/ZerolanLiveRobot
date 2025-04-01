import json
from typing import Callable, Union, List, Dict

from loguru import logger
from pydantic import BaseModel
from websockets import ConnectionClosed
from websockets.sync.connection import Connection
from websockets.sync.server import serve, Server

from common.concurrent.abs_runnable import ThreadRunnable


############################
#  Json Web Socket Server  #
# Author: AkagawaTsurunaki #
############################

class JsonWsServer(ThreadRunnable):
    def __init__(self, host: str, port: int, subprotocols: List[str] = None):
        super().__init__()
        self.ws: Server | None = None
        self.host = host
        self.port = port
        # 重要！使用子协议用于校验！
        self.subprotocols = subprotocols

        # 监听器注册
        self.on_msg_handlers: List[Callable[[Connection, Union[Dict, List]], None]] = []
        self.on_open_handlers: List[Callable[[Connection], None]] = []
        self.on_close_handlers: List[Callable[[Connection, int, str], None]] = []
        self.on_err_handlers: List[Callable[[Connection, Exception], None]] = []

        # Connection 记录（关闭连接后不要使用 Connection 对象）
        self._connections: dict[Connection, str] = {}

    def name(self):
        return "JsonWsServer"

    def start(self):
        super().start()
        with serve(handler=self._handle_json_recv, host=self.host, port=self.port,
                   subprotocols=self.subprotocols) as ws:
            self.ws = ws
            logger.info(f"WebSocket server started at {self.host}:{self.port}")
            self.ws.serve_forever()

    def stop(self):
        super().stop()
        if self.ws is not None:
            self.ws.shutdown()

    @property
    def connections(self):
        return len(self._connections)

    def _handle_json_recv(self, ws: Connection):
        """处理每个 WebSocket 连接"""
        # 处理 Sec-WebSocket-Protocol 的 Header
        self._validate_subprotocols(ws)
        self._add_connection(ws)
        try:
            while True:
                try:
                    message = ws.recv()
                    data = json.loads(message)
                    # 注意：这里一旦抛出异常，那么并非所有的 Handler 都会被执行
                    # 例如说，有 10 个 Handler，如果第 5 个出错，那么后 5 个将不会被执行
                    for handler in self.on_msg_handlers:
                        handler(ws, data)
                except Exception as e:
                    if isinstance(e, ConnectionClosed):
                        raise e
                    if len(self.on_err_handlers) == 0:
                        logger.exception(e)
                    self._handle_exception(ws, e)

        except ConnectionClosed as e:
            self._remove_connection(ws, e)

    def _validate_subprotocols(self, ws: Connection):
        if ws.subprotocol is not None:
            if ws.subprotocol not in self.subprotocols:
                logger.warning(f"Not supported sub protocol: {ws.id} {ws.remote_address}")
                raise ValueError(f"Not supported sub protocol: {ws.id} {ws.remote_address}")

    def _add_connection(self, ws: Connection):
        self._connections[ws] = str(ws.id)
        for handler in self.on_open_handlers:
            handler(ws)
        logger.info(f"WebSocket client connected: {ws.id} {ws.remote_address}")

    def _remove_connection(self, ws: Connection, e: ConnectionClosed):
        ws_id = self._connections.pop(ws)
        for handler in self.on_close_handlers:
            handler(ws, e.rcvd.code, e.rcvd.reason)
        logger.warning(f"WebSocket client disconnected: {ws_id}")

    def _handle_exception(self, ws: Connection, e: Exception):
        for handler in self.on_err_handlers:
            handler(ws, e)

    def send_json(self, data: any):
        if isinstance(data, BaseModel):
            msg = data.model_dump_json(indent=4)
        else:
            msg = json.dumps(data, ensure_ascii=False, indent=4)

        for conn in self._connections:
            conn.send(msg)
