import asyncio
from asyncio import TaskGroup

import pytest

from manager.model_manager import ModelManager
from services.playground.bridge import PlaygroundBridge

_bridge = PlaygroundBridge(host="127.0.0.1", port=11013)

auto_close_flag = False


@pytest.mark.asyncio
async def test_conn():
    async with TaskGroup() as tg:
        start_task = tg.create_task(_bridge.start())
        if auto_close_flag:
            await asyncio.sleep(2)
            print("Closing the WebSocket server")
            await _bridge.stop()
            start_task.cancel()

@pytest.mark.asyncio
async def test_load_3d_model():
    async with TaskGroup() as tg:
        tg.create_task(test_conn())
        _manager = ModelManager("../resources/static/models/3d")
        await _manager.scan()
        file_id = _manager.get_files()[0]["id"]
        file_info = _manager.get_file_by_id(file_id)
        while not _bridge.is_connected:
            await asyncio.sleep(0.1)
        await _bridge.load_3d_model(file_info)
