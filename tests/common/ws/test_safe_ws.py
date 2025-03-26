import time

from google.protobuf.any_pb2 import Any as ProtoBufAny  # type: ignore
from websockets.sync.client import connect

from common.killable_thread import KillableThread
from common.utils.pws_util import do_challenge
from common.ws.proto.protocol_pb2 import ZerolanProtocol, ServerHello, ClientHello  # type: ignore
from common.ws.safe_zrl_ws import SafeZerolanProtocolWebSocketServer, BaseAction


def test_safe_zrl_ws():
    password = "js8632gd8s9j"
    ws = SafeZerolanProtocolWebSocketServer(host="0.0.0.0", port=5684, password=password)

    thread = KillableThread(target=ws.start, daemon=True)
    thread.start()
    uri = "ws://127.0.0.1:5684"
    time.sleep(1)

    with connect(uri, subprotocols=["ZerolanProtocol"]) as websocket:
        response = websocket.recv()
        print(response)
        response_msg = ZerolanProtocol()
        response_msg.ParseFromString(response)
        print(response_msg)
        server_hello = ServerHello()
        assert response_msg.data.Unpack(server_hello)
        auth = do_challenge(password, server_hello.salt, server_hello.challenge)

        any_data = ProtoBufAny()
        any_data.Pack(ClientHello(auth=auth, namespace="Test"))

        zp = ZerolanProtocol(
            protocol="ZerolanProtocol",
            version="1.1",
            action=BaseAction.CLIENT_HELLO,
            code=0,
            message="Client hello",
            data=any_data
        )

        websocket.send(zp.SerializeToString())
        time.sleep(2)
        thread.kill()
