"""
Web Socket Server ver.2
Author: AkagawaTsurunaki
"""

from abc import abstractmethod
from typing import List, Callable, Any, Iterable

from loguru import logger
from websockets import ConnectionClosed, Data
from websockets.sync.connection import Connection
from websockets.sync.server import Server, serve

from common.abs_runnable import ThreadRunnable


class BaseWebSocketServer(ThreadRunnable):
    @abstractmethod
    def name(self):
        raise NotImplementedError()

    def __init__(self, host: str, port: int, subprotocols: List[str] = None):
        """
        Base WebSocket Server.
        :param host: The host of the WebSocket server.
        :param port: The port of the WebSocket server.
        :param subprotocols: Subprotocols to use.
        """
        super().__init__()
        self.server: Server | None = None
        self.host = host
        self.port = port
        # Important! Use sub-protocols for validation!
        self.subprotocols = subprotocols

        # Listeners are registered here.
        self.on_msg_handlers: List[Callable[[Connection, Any], None]] = []
        self.on_open_handlers: List[Callable[[Connection], None]] = []
        self.on_close_handlers: List[Callable[[Connection, int, str], None]] = []
        self.on_err_handlers: List[Callable[[Connection, Exception], None]] = []

        # WebSockets Connections (do not use the Connection object after closing the connection)
        self._connections: dict[Connection, str] = {}

    def start(self):
        super().start()
        with serve(handler=self._handle_msg_recv, host=self.host, port=self.port,
                   subprotocols=self.subprotocols) as server:
            self.server = server
            self.server.serve_forever()

    def stop(self):
        super().stop()
        if self.server is not None:
            self.server.shutdown()

    @property
    def connections(self):
        return len(self._connections)

    def _handle_msg_recv(self, connection: Connection):
        """
        Handle every WebSocket connection.

        :param connection: WebSocket Connection.
        """

        self._add_connection(connection)
        while True:
            try:
                exceptions = []
                message = connection.recv()
                for handler in self.on_msg_handlers:
                    try:
                        handler(connection, message)
                    except Exception as e:
                        exceptions.append(e)
                for e in exceptions:
                    self._handle_exception(connection, e)
            except ConnectionClosed as e:
                self._remove_connection(connection, e)
                logger.warning("Disconnect")
                return
            except Exception as e:
                if isinstance(e, ConnectionClosed):
                    raise e
                self._handle_exception(connection, e)

    def _add_connection(self, connection: Connection):
        self._connections[connection] = str(connection.id)
        for handler in self.on_open_handlers:
            handler(connection)
        logger.info(f"WebSocket client connected: {connection.id} {connection.remote_address}")

    def _remove_connection(self, connection: Connection, e: ConnectionClosed):
        ws_id = self._connections.pop(connection)
        for handler in self.on_close_handlers:
            code = -1
            reason = "???"
            if e.rcvd is not None:
                code = e.rcvd.code
                reason = e.rcvd.reason
            handler(connection, code, reason)
        logger.warning(f"WebSocket client disconnected: {ws_id}")

    def _handle_exception(self, connection: Connection, e: Exception):
        if len(self.on_err_handlers) == 0:
            logger.exception(e)
            return
        for handler in self.on_err_handlers:
            handler(connection, e)

    def on_message(self, *args, **kwargs):
        def decorator(func: Callable[[Connection, Any], None]):
            self.on_msg_handlers.append(func)
            logger.debug(f"Function `{func.__name__}` has been registered as OnMessageListener.`")

        return decorator

    def on_close(self, *args, **kwargs):
        def decorator(func: Callable[[Connection, int, str], None]):
            self.on_close_handlers.append(func)
            logger.debug(f"Function `{func.__name__}` has been registered as OnCloseListener.`")

        return decorator

    def on_open(self, *args, **kwargs):
        def decorator(func: Callable[[Connection], None]):
            self.on_open_handlers.append(func)
            logger.debug(f"Function `{func.__name__}` has been registered as OnOpenListener.`")

        return decorator

    def on_error(self, *args, **kwargs):
        def decorator(func: Callable[[Connection, Exception], None]):
            self.on_err_handlers.append(func)
            logger.debug(f"Function `{func.__name__}` has been registered as OnErrorListener.`")

        return decorator

    def send(self, message: Data | Iterable[Data], text: bool | None = None):
        """
        Send message to all connected clients.
        :param message: Data.
        :param text: Whether to send as text.
        """
        for conn in self._connections:
            conn.send(message, text)
        print(message)
