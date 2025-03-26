"""
Json Web Socket Server ver.2
Author: AkagawaTsurunaki
"""
import json
from typing import List, Any, Type

from pydantic import BaseModel

from common.ws.base_ws import BaseWebSocketServer


class JsonWebSocketServer(BaseWebSocketServer):

    def __init__(self, host: str, port: int, subprotocols: List[str] = None):
        super().__init__(host, port, subprotocols)

    def name(self):
        return "JsonWebSocketServer"

    def on_message(self, base_model_type: Type[BaseModel]):
        """
        On instance of BaseModel received.
        :param base_model_type: Type of BaseModel.
        :return: Decorator.
        """

        def decorator(func):
            @super(JsonWebSocketServer, self).on_message()
            def wrapper(connection, message):
                instance = base_model_type.model_validate_json(message)
                assert isinstance(instance, base_model_type)
                func(connection, instance)

        return decorator

    def send(self, message: Any):  # noqa
        """
        Send json data to all connected clients.
        :param message: Instance of BaseModel or object that can be dumped as json string.
        """
        if isinstance(message, BaseModel):
            msg = message.model_dump_json(indent=4)
        else:
            msg = json.dumps(message, ensure_ascii=False, indent=4)

        for conn in self._connections:
            conn.send(msg)
