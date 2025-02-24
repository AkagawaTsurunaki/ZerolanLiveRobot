from zerolan.data.protocol.protocol import ZerolanProtocol

from common.web.zrl_ws import ZerolanProtocolWsServer

_test = {
    "protocol": "ZerolanProtocol",
    "version": "1.1",
    "message": "Ciallo",
    "code": 0,
    "action": "Onanii",
    "data": {
        "frequency": 114514,
        "hand": "right"
    }
}


class TestZwsImpl(ZerolanProtocolWsServer):

    def on_protocol(self, protocol: ZerolanProtocol):
        print(protocol)
        assert protocol.data["frequency"] == _test["data"]["frequency"]
        assert protocol.data["hand"] == _test["data"]["hand"]
        self.send(action="Ciallo", message="Kimochii~", data={"aieki": 100, "love": 100})

    def on_disconnect(self, ws_id: str):
        print(ws_id)


def test_zws():
    server = TestZwsImpl(host='127.0.0.1', port=11013)
    server.start()
