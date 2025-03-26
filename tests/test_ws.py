import json
import time

from pydantic import BaseModel
from websockets.sync.client import connect

from common.killable_thread import KillableThread
from common.ws.json_ws import JsonWebSocketServer
from common.ws.protoc_ws import ProtoBufWebSocketServer
from services.playground.proto import message_pb2


class MyMessage(BaseModel):
    msg: str = "asdasd"
    code: int = 114


def test_json_ws():
    ws = JsonWebSocketServer(host="0.0.0.0", port=5684, subprotocols=["ZerolanProtocol"])

    @ws.on_message(MyMessage)
    def some(_, data_msg: MyMessage):
        print(f"Received message: {data_msg.msg}, code: {data_msg.code}")

        data_msg.code = 514
        data_msg.msg = "dsadsa"

        ws.send(data_msg)

    thread = KillableThread(target=ws.start, daemon=True)
    thread.start()
    uri = "ws://127.0.0.1:5684"
    time.sleep(1)
    with connect(uri, subprotocols=["ZerolanProtocol"]) as websocket:
        data_msg = MyMessage()
        websocket.send(data_msg.model_dump_json())

        response = websocket.recv()
        data = json.loads(response)
        print(f"Received response: {data['msg']}, code: {data['code']}")

        thread.kill()


def test_send_message():
    ws = ProtoBufWebSocketServer(host="0.0.0.0", port=5684, subprotocols=["ZerolanProtocol"])

    @ws.on_message(message_pb2.DataMessage)
    def some(_, data_msg: message_pb2.DataMessage):
        print(f"Received message: {data_msg.content}, ID: {data_msg.id}")

        response = message_pb2.DataMessage()
        response.content = "Server response"
        response.id = 1001

        ws.send(response)

    thread = KillableThread(target=ws.start, daemon=True)
    thread.start()
    uri = "ws://127.0.0.1:5684"
    time.sleep(1)
    with connect(uri, subprotocols=["ZerolanProtocol"]) as websocket:
        data_msg = message_pb2.DataMessage()
        data_msg.content = "Hello, Server!"
        data_msg.id = 42
        with open(r"resources/tts-test.wav", mode='rb') as f:
            data_msg.data = f.read()

        websocket.send(data_msg.SerializeToString())

        response = websocket.recv()
        response_msg = message_pb2.DataMessage()
        response_msg.ParseFromString(response)

        print(f"Received response: {response_msg.content}, ID: {response_msg.id}")

        thread.kill()
