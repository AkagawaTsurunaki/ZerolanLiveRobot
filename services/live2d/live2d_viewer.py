import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue

import live2d.v3 as live2d
from PyQt5.QtWidgets import QApplication
from pydantic import BaseModel, Field
from typeguard import typechecked

from common.concurrent.abs_runnable import ThreadRunnable
from common.concurrent.killable_thread import KillableThread
from services.live2d.live2d_canvas import Live2DCanvas


class Live2DViewerConfig(BaseModel):
    model3_json_file: str = Field(default="./resources/static/models/live2d", description="Path of `xxx.model3.json`")


class Live2DViewer(ThreadRunnable):
    def name(self):
        return "Live2DViewer"

    def __init__(self, config: Live2DViewerConfig):
        super().__init__()
        self._model_path = config.model3_json_file
        self._canvas: Live2DCanvas | None = None
        self._audios: Queue[Path] = Queue()
        self._sync_lip_loop_thread = KillableThread(target=self._sync_lip_loop, daemon=True)
        self._sync_lip_loop_flag = True

    def start(self):
        super().start()
        live2d.init()
        app = QApplication(sys.argv)
        self._canvas = Live2DCanvas(self._model_path)
        self._sync_lip_loop_thread.start()
        self._canvas.show()
        app.exec()
        live2d.dispose()

    def _sync_lip_loop(self):
        while self._sync_lip_loop_flag:
            audio_path = self._audios.get(block=True)
            self._canvas.sync_lip(str(audio_path))

    def stop(self):
        super().stop()
        self._sync_lip_loop_flag = False
        self._sync_lip_loop_thread.kill()

    @typechecked
    def sync_lip(self, audio_path: Path):
        """
        Sync the lip of the character.
        Note: This method will NOT block your thread!
              For example, if you have 2 audio files to play and sync lip,
              You should play the second after the first finished.
        :param audio_path: The path of the audio file.
        """
        assert audio_path.exists()
        self._audios.put(audio_path)
