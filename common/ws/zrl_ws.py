"""
Zerolan Protocol Web Socket Server
Author: AkagawaTsurunaki
"""
from typing import Any
from google.protobuf.any_pb2 import Any as ProtoBufAny # type: ignore
from websockets import ProtocolError

from common.ws.protoc_ws import ProtoBufWebSocketServer
from services.playground.proto import message_pb2


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
        protocol_obj = message_pb2.ZerolanProtocol(protocol=self._protocol, # type: ignore
                                                   version=self._version,
                                                   message=message,
                                                   code=code,
                                                   action=action,
                                                   data=any_data)
        super().send(protocol_obj)

    def on_message(self, protoc_type: Any):
        def decorator(func):
            @super(ZerolanProtocolWebSocket, self).on_message(protoc_type)
            def wrapper(connection, message):
                assert isinstance(message, protoc_type)
                if message.protocol == self._protocol and message.version == self._version:
                    func(connection, message)
                else:
                    raise ProtocolError("Invalid ZerolanProtocol. Check the protocol name and the version.")

        return decorator
