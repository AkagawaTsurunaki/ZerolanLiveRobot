import os.path
import time
from pathlib import Path

from common.concurrent.killable_thread import KillableThread
from manager.config_manager import get_project_dir
from services.live2d.live2d_viewer import Live2DViewer
from services.live2d.config import Live2DViewerConfig

_dir = get_project_dir()
_model_file = os.path.join(_dir,
                           r"resources/static/models/live2d/hiyori_pro_zh/hiyori_pro_zh/runtime/hiyori_pro_t11.model3.json")
_audio_path = "resources/tts-test.wav"


def test_live2d():
    config = Live2DViewerConfig(
        model3_json_file=_model_file)
    viewer = Live2DViewer(config)
    t = KillableThread(target=viewer.start)
    t.start()
    time.sleep(1)
    viewer.sync_lip(Path(_audio_path))
    time.sleep(2)
    viewer.sync_lip(Path(_audio_path))
    time.sleep(10)
    t.kill()
