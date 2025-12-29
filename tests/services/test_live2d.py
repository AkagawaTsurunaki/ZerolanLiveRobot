import asyncio
from pathlib import Path

import pytest
from loguru import logger

from common.concurrent.killable_thread import KillableThread
from manager.config_manager import get_project_dir, get_config
from services.live2d.live2d_viewer import Live2DViewer
from services.live2d.config import Live2DViewerConfig

_dir = get_project_dir()
print(_dir)
_config = get_config()
_audio_path = Path(_dir).joinpath("tests/resources/tts-test.wav")


@pytest.mark.asyncio
async def test_live2d():
    config = Live2DViewerConfig(
        model3_json_file=_config.service.live2d_viewer.model3_json_file)
    viewer = Live2DViewer(config)
    t = KillableThread(target=viewer.start)
    t.start()
    await asyncio.sleep(1)
    logger.info("First speech")
    viewer.sync_lip(Path(_audio_path))
    await asyncio.sleep(2)
    logger.info("Second speech")
    viewer.sync_lip(Path(_audio_path))
    await asyncio.sleep(10)
    logger.info("Stopping")
    viewer.stop()
    t.kill()
