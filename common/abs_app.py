from abc import ABC, abstractmethod
from dataclasses import dataclass

from flask import Flask, jsonify


@dataclass
class AppStatus:
    status: str


class AppStatusEnum:
    OK = "ok"
    STOPPED = "stopped"
    INITIALIZING = "initializing"


class AbstractApplication(ABC):

    def __init__(self, name: str):
        self.name = name
        self.status = AppStatusEnum.STOPPED
        self._app = Flask(__name__)
        self._app.add_url_rule(rule=f'/{self.name}/status', view_func=self._handle_status,
                               methods=["GET", "POST"])

    def _handle_status(self):
        return jsonify(AppStatus(status=self.status))

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def _handle_predict(self):
        pass

    @abstractmethod
    def _handle_stream_predict(self):
        pass
