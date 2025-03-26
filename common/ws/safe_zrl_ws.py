from enum import Enum
from typing import Dict, Any, Callable, List

from loguru import logger
from websockets.frames import CloseCode
from websockets.sync.connection import Connection

from common.utils.pws_util import generate_salt, generate_challenge, do_challenge
from common.ws.proto.protocol_pb2 import ServerHello, ClientHello  # type: ignore
from common.ws.zrl_ws import ZerolanProtocolWebSocket


class BaseAction(str, Enum):
    CLIENT_HELLO = "client_hello"
    SERVER_HELLO = "server_hello"


class SafeZerolanProtocolWebSocketServer(ZerolanProtocolWebSocket):

    def __init__(self, host: str, port: int, password: str):
        """

        WebSocket server that implemented ZerolanProtocol based on Google's ProtoBuf.
        Use WebSocket sub-protocol "ZerolanProtocol".
        Connection must be verified before more operations.

        ## How to Verify the client identity?

        Server will send SeverHello to the connected client.
        And the connected client must do challenge and send authentication code to server.
        After server verified the authentication code, the client can send more operations or data to server.
        If the authentication code is incorrect, server will close the connection immediately.
        Or if client send other data without verifying it at first, server will close the connection immediately.

        Server will send challenge and salt.
        Client can get authentication code by:
        ```python
            base64_secret = generate_base64_secret(password + salt)
            my_auth = generate_base64_secret(base64_secret + challenge)
        ```
        where,
        ```python
        def generate_base64_secret(data: str) -> str:
            sha256_hash = hashlib.sha256(data.encode('utf-8')).digest()
            base64_encoded_hash = base64.b64encode(sha256_hash).decode('utf-8')
        ```
        """
        super().__init__(host, port)
        self._password = password
        self.challenges: Dict[Connection, str] = {}
        self.verified_conns = []
        self.on_verified_handlers: List[Callable[[Connection, ClientHello], None]] = []
        self.init()

    def init(self):

        @self.on_open()
        def on_connect(conn: Connection):
            salt = generate_salt()
            challenge = generate_challenge()
            dto = ServerHello(salt=salt, challenge=challenge)
            self.send(action=BaseAction.SERVER_HELLO, data=dto, message="Please verify your identity.")
            self.challenges[conn] = do_challenge(self._password, salt, challenge)

        @super(SafeZerolanProtocolWebSocketServer, self).on_message(action=BaseAction.CLIENT_HELLO,
                                                                    data_type=ClientHello)
        def verify_connection(conn: Connection, client_hello: ClientHello):
            logger.debug("Verifying connection...")
            auth = self.challenges.get(conn, None)
            assert auth is not None, f"Auth string should be generated!"
            if auth == client_hello.auth:
                self.challenges.pop(conn, None)
                self.verified_conns.append(conn)
                logger.info(f"Connection {conn.id} verified!")
                for handler in self.on_verified_handlers:
                    handler(conn, client_hello)
            else:
                conn.close(CloseCode.NORMAL_CLOSURE, reason="Challenge failure. Closed.")
                logger.warning("Failed to verify client identity. Closed.")

        @self.on_close()
        def on_disconnect(conn: Connection, code: int, reason: str):
            try:
                self.challenges.pop(conn, None)
                self.verified_conns.remove(conn)
            except ValueError:
                logger.warning("A unverified connection is closed.")
            else:
                logger.warning(f"A verified connection is closed: ({code}) {reason}")

    def on_verified(self):
        def decorator(func: Callable[[Connection, ClientHello], None]):
            self.on_verified_handlers.append(func)

        return decorator

    def on_message(self, data_type: Any, action: str):
        def decorator(func):
            @super(SafeZerolanProtocolWebSocketServer, self).on_message(data_type, action)
            def on_safe_zp_message(connection, message):
                if connection in self.verified_conns:
                    func(connection, message)
                else:
                    connection.close(CloseCode.NORMAL_CLOSURE, reason="Unverified connection. Closed.")
                    logger.warning("Illegal operation for unverified connection. Closed.")

        return decorator
