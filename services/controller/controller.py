from urllib.parse import urljoin

import requests
from flask import Flask, jsonify, request
from injector import inject
from pydantic import BaseModel

from common.config import ControllerConfig
from event.event_data import SwitchVADEvent
from event.eventemitter import emitter


class HTTPResponse(BaseModel):
    msg: str
    data: dict | None = None


class ControllerWebServer:
    def __init__(self, config: ControllerConfig):
        self.app = Flask(__name__)
        self._host = config.host
        self._port = config.port
        self._setup_routes()

    def _setup_routes(self):
        # To test connection
        @self.app.route('/')
        def home():
            return "Successful connect"

        # Switch the VAD service to on/off
        @self.app.route('/controller/service/vad', methods=['PATCH'])
        def switch_vad():
            emitter.emit(SwitchVADEvent(switch=request.json['switch']))
            return jsonify(HTTPResponse(msg="切换麦克风状态").model_dump())

    def run(self):
        self.app.run(host=self._host, port=self._port)


class ZerolanController:

    @inject
    def __init__(self, url: str):
        self._url = url

    def switch_microphone(self):
        requests.patch(urljoin(self._url, "/controller/service/vad"), json={"switch": None})
