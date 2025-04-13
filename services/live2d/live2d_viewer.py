

import sys

import live2d.v3 as live2d
from PyQt5.QtWidgets import QApplication
from pydantic import BaseModel, Field

from common.concurrent.abs_runnable import ThreadRunnable
from services.live2d.live2d_canvas import Live2DCanvas


class Live2DViewerConfig(BaseModel):
    model3_json_file: str = Field(default="./resources/static/models/live2d", description="Path of `xxx.model3.json`")


class Live2DViewer(ThreadRunnable):
    def name(self):
        return "Live2DViewer"

    def start(self):
        super().start()
        live2d.init()
        app = QApplication(sys.argv)
        win = Live2DCanvas(self._model_path)
        win.show()
        app.exec()
        live2d.dispose()

    def stop(self):
        super().stop()

    def __init__(self, config: Live2DViewerConfig):
        super().__init__()
        self._model_path = config.model3_json_file
