"""
ProtoBuf Web Socket Server ver.2
Author: AkagawaTsurunaki
"""
from typing import List, Any

from common.ws.base_ws import BaseWebSocketServer


class ProtoBufWebSocketServer(BaseWebSocketServer):

    def __init__(self, host: str, port: int, subprotocols: List[str] = None):
        super().__init__(host, port, subprotocols)

    def name(self):
        return "ProtocWebSocketServer"

    def on_message(self, protoc_type: Any):
        def decorator(func):
            @super(ProtoBufWebSocketServer, self).on_message()
            def wrapper(connection, message):
                instance = protoc_type()
                instance.ParseFromString(message)
                assert isinstance(instance, protoc_type)
                func(connection, instance)

        return decorator

    def send(self, message: Any):  # noqa
        assert hasattr(message, "SerializeToString")
        message = message.SerializeToString()
        super().send(message)
