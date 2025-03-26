"""
ProtoBuf Web Socket Server ver.2
Author: AkagawaTsurunaki
"""
from typing import List, Any

from loguru import logger

from common.ws.base_ws import BaseWebSocketServer


class ProtoBufWebSocketServer(BaseWebSocketServer):

    def __init__(self, host: str, port: int, subprotocols: List[str] = None):
        super().__init__(host, port, subprotocols)

    def name(self):
        return "ProtocWebSocketServer"

    def on_message(self, protoc_type: Any):
        def decorator(func):
            @super(ProtoBufWebSocketServer, self).on_message()
            def on_pb_message_wrapper(connection, message):
                instance = protoc_type()
                instance.ParseFromString(message)
                assert isinstance(instance, protoc_type)
                func(connection, instance)

            logger.debug(f"Function {func.__name__} is registered as OnProtoBufMessageListener")

        return decorator

    def send(self, message: Any):  # noqa
        assert hasattr(message, "SerializeToString")
        message = message.SerializeToString()
        super().send(message)
