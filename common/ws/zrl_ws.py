"""
Zerolan Protocol Web Socket Server
Author: AkagawaTsurunaki
"""
from typing import Any

from google.protobuf.any_pb2 import Any as ProtoBufAny  # type: ignore
from loguru import logger
from websockets import ProtocolError

from common.ws.proto.protocol_pb2 import ZerolanProtocol  # type: ignore
from common.ws.protoc_ws import ProtoBufWebSocketServer


class ZerolanProtocolWebSocket(ProtoBufWebSocketServer):
    def __init__(self, host: str, port: int):
        self._protocol = "ZerolanProtocol"
        super().__init__(host, port, subprotocols=[self._protocol])
        self._version = "1.1"

    def name(self):
        return "ZerolanProtocolBridge"

    @property
    def is_connected(self):
        return self.connections > 0

    def send(self, action: str, data: any, message: str = "", code: int = 0):  # noqa
        any_data = ProtoBufAny()
        any_data.Pack(data)
        protocol_obj = ZerolanProtocol(protocol=self._protocol,
                                       version=self._version,
                                       message=message,
                                       code=code,
                                       action=action,
                                       data=any_data)
        super().send(protocol_obj)

    def on_message(self, data_type: Any, action: str):  # noqa
        def decorator(func):
            @super(ZerolanProtocolWebSocket, self).on_message(ZerolanProtocol)
            def on_zp_message(connection, message):
                logger.debug("Test on_message")
                assert isinstance(message, ZerolanProtocol)
                if message.protocol == self._protocol and message.version == self._version:
                    if message.action == action:
                        data = data_type()
                        message.data.Unpack(data)
                        func(connection, data)
                else:
                    raise ProtocolError("Invalid ZerolanProtocol. Check the protocol name and the version.")

            logger.debug(f"Function {func.__name__} is registered as OnZerolanProtocolMessageListener")

        return decorator
