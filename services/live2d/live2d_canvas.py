"""
Copied and modified from https://github.com/Arkueid/live2d-py/blob/main/package/main_pyqt5_canvas_opacity.py
"""

import math
from typing import Tuple

import live2d.v3 as live2d
from PyQt5.QtCore import Qt
from live2d.v3 import StandardParams

from common.ver_check import is_live2d_py_version_less_than
from services.live2d.opengl_canvas import OpenGLCanvas
from services.live2d.wave_handler import Live2DWaveHandler


class Live2DCanvas(OpenGLCanvas):
    def __init__(self, path: str, lip_sync_n: int = 3, win_size: Tuple[int, int] = (1920, 1080)):
        super().__init__()
        self.setFixedSize(*win_size)
        self._model_path = path
        self._lipSyncN = lip_sync_n

        self.wavHandler = Live2DWaveHandler()
        self.model: None | live2d.LAppModel = None
        self.setWindowTitle("Live2DCanvas")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.radius_per_frame = math.pi * 0.5 / 120
        self.total_radius = 0

    def on_init(self):
        # live2d-py 6.0 remove glewInit()
        if is_live2d_py_version_less_than("6.0"):
            live2d.glewInit()
        else:
            raise NotImplementedError("Unsupported `live2d-py` version detected. Version 5.0 is required")
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
        if self.wavHandler.Update():
            # Use the loudness of the WAV to update mouth opening and closing.
            self.model.SetParameterValue(
                StandardParams.ParamMouthOpenY, self.wavHandler.GetRms() * self._lipSyncN
            )
            # logger.debug(f"Rms: {self.wavHandler.GetRms()}")
        self.model.Update()
        self.model.Draw()

    def on_resize(self, width: int, height: int):
        self.model.Resize(width, height)
