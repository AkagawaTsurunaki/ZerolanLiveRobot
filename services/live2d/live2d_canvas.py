"""
Copied and modified from https://github.com/Arkueid/live2d-py/blob/main/package/main_pyqt5_canvas_opacity.py
"""

import math

import live2d.v3 as live2d
from PyQt5.QtCore import Qt
from live2d.utils.lipsync import WavHandler
from live2d.v3 import StandardParams

from services.live2d.opengl_canvas import OpenGLCanvas


class Live2DCanvas(OpenGLCanvas):
    def __init__(self, path: str, lip_sync_n: int = 3):
        super().__init__()
        self._model_path = path
        self._lipSyncN = lip_sync_n

        self._wavHandler = WavHandler()
        self.model: None | live2d.LAppModel = None
        self.setWindowTitle("Live2DCanvas")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.radius_per_frame = math.pi * 0.5 / 120
        self.total_radius = 0

    def on_init(self):
        live2d.glewInit()
        self.model = live2d.LAppModel()
        if live2d.LIVE2D_VERSION == 3:
            self.model.LoadModelJson(self._model_path)
        else:
            self.model.LoadModelJson(self._model_path)
        self.startTimer(int(1000 / 120))

    def timerEvent(self, a0):
        self.update()

    def on_draw(self):
        live2d.clearBuffer()
        if self._wavHandler.Update():
            # 利用 wav 响度更新 嘴部张合
            self.model.SetParameterValue(
                StandardParams.ParamMouthOpenY, self._wavHandler.GetRms() * self._lipSyncN
            )
        self.model.Update()
        self.model.Draw()

    def sync_lip(self, audio_path: str):
        self._wavHandler.Start(audio_path)

    def on_resize(self, width: int, height: int):
        self.model.Resize(width, height)
