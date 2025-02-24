import time
from concurrent.futures.thread import ThreadPoolExecutor
from json import JSONDecodeError
from typing import Union, List, Dict

from pydantic import BaseModel
from websockets.sync.connection import Connection

from common.web.json_ws import JsonWsServer


class TestA(BaseModel):
    msg: str
    num: int


def test_jws():
    host = "localhost"
    port = 11013
    print(f"Starting WebSocket server on ws://{host}:{port}")
    jws = JsonWsServer(host, port, ["ZerolanProtocol"])

    sender = ThreadPoolExecutor(max_workers=1)

    def on_open(ws: Connection):
        def send_ciallo():
            while True:
                ws.send("Server Ciallo！")
                time.sleep(1)

        sender.submit(send_ciallo)
        print(f"{ws.remote_address} => Client Ciallo!")

    def on_msg(ws: Connection, json: Union[Dict, List]):
        s = TestA.model_validate(json)
        print(f"{ws.remote_address} => msg: {s}")

    def on_err(ws: Connection, err: Exception):
        if isinstance(err, JSONDecodeError):
            ws.send("Error json")
        else:
            print(f"{ws.remote_address} => error: {err}")

    def on_close(_: Connection, code: int, reason: str):
        print(f"A client closed: ({code}) {reason}")

    jws.on_msg_handlers += [on_msg]
    jws.on_open_handlers += [on_open]
    jws.on_close_handlers += [on_close]
    jws.on_err_handlers += [on_err]

    jws.start()
