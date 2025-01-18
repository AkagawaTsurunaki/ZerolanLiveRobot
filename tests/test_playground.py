import asyncio
from asyncio import TaskGroup

import pytest

from common.config import get_config
from common.data import LoadLive2DModelDTO
from manager.model_manager import ModelManager
from services.playground.bridge import PlaygroundBridge

_bridge = PlaygroundBridge(host="127.0.0.1", port=11013)

auto_close_flag = False


async def syncwait():
    while not _bridge.is_connected:
        await asyncio.sleep(0.1)


# You can test the connection to ZerolanPlayground
# All test cases will depend on this function so make sure you test it at first.
@pytest.mark.asyncio
async def test_conn():
    async with TaskGroup() as tg:
        start_task = tg.create_task(_bridge.start())
        if auto_close_flag:
            await asyncio.sleep(2)
            print("Closing the WebSocket server")
            await _bridge.stop()
            start_task.cancel()


# You should put at least 1 3D-model file under `../resources/static/models/3d`,
# Or the test case will not work.
# You can also change the path if you want.
@pytest.mark.asyncio
async def test_load_3d_model():
    async with TaskGroup() as tg:
        tg.create_task(test_conn())
        _manager = ModelManager("../resources/static/models/3d")
        await _manager.scan()
        file_id = _manager.get_files()[0]["id"]
        file_info = _manager.get_file_by_id(file_id)
        await syncwait()
        await _bridge.load_3d_model(file_info)


_config = get_config()


# You should set Live2D-model file path in your config.yaml
# Or the test case will not work.
@pytest.mark.asyncio
async def test_load_live2d_model():
    async with TaskGroup() as tg:
        tg.create_task(test_conn())
        model_dir = _config.service.playground.model_dir
        bot_id = _config.service.playground.bot_id
        await syncwait()
        await _bridge.load_live2d_model(
            LoadLive2DModelDTO(bot_id=bot_id, model_dir=model_dir, bot_display_name="Koneko"))
