from abc import abstractmethod

from loguru import logger
from websockets import ProtocolError
from zerolan.data.protocol.protocol import ZerolanProtocol

from common.concurrent.abs_runnable import ThreadRunnable
from common.web.json_ws import JsonWsServer


########################################
#  Zerolan Protocol Web Socket Server  #
#       Author: AkagawaTsurunaki       #
########################################

class ZerolanProtocolWsServer(ThreadRunnable):
    def __init__(self, host: str, port: int):
        super().__init__()
        self._protocol = "ZerolanProtocol"
        self._jws = JsonWsServer(host=host, port=port, subprotocols=[self._protocol])
        self._version = "1.1"

    def name(self):
        return "ZerolanProtocolWebsocket"

    def start(self):
        super().start()
        self._init()
        self._jws.start()

    def stop(self):
        super().stop()
        self._jws.stop()

    @property
    def is_connected(self):
        if self._jws.connections > 0:
            return True
        return False

    def send(self, action: str, data: any, message: str = "", code: int = 0):
        protocol = ZerolanProtocol(message=message,
                                   code=code,
                                   action=action,
                                   data=data)
        self._jws.send_json(protocol)

    def _init(self):
        def on_json_msg(_, protocol: dict | list):
            protocol = self._validate_zerolan_protocol(protocol)
            logger.debug(f"Validated Zerolan Protocol {protocol.data}")
            self.on_protocol(protocol)

        self._jws.on_msg_handlers += [on_json_msg]

    def _validate_zerolan_protocol(self, data: dict | list):
        recv_obj = ZerolanProtocol.model_validate(data)
        if recv_obj.protocol == self._protocol and recv_obj.version == self._version:
            return recv_obj
        raise ProtocolError("Invalid ZerolanProtocol")

    @abstractmethod
    def on_protocol(self, protocol: ZerolanProtocol):
        raise NotImplementedError()

    @abstractmethod
    def on_disconnect(self, ws_id: str):
        raise NotImplementedError()
