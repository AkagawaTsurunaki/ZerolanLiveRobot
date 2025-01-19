import asyncio
from asyncio import TaskGroup

import pytest

from common.config import get_config
from common.data import LoadLive2DModelDTO, CreateGameObjectDTO, GameObjectType, Transform, Position, ScaleOperationDTO
from manager.model_manager import ModelManager
from services.playground.bridge import PlaygroundBridge

_config = get_config()
_bridge = PlaygroundBridge(_config.service.playground)

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


async def create_sphere():
    await _bridge.create_gameobject(
        CreateGameObjectDTO(instance_id=114, game_object_name="MySphere", object_type=GameObjectType.SPHERE,
                            color="#114514", transform=Transform(scale=5.0, position=Position(x=1, y=1, z=1))))


@pytest.mark.asyncio
async def test_create_gameobject():
    async with TaskGroup() as tg:
        tg.create_task(test_conn())
        await syncwait()
        await create_sphere()


@pytest.mark.asyncio
async def test_modify_game_object_scale():
    async with TaskGroup() as tg:
        tg.create_task(test_conn())
        await syncwait()
        await create_sphere()
        await asyncio.sleep(1)
        for e in _bridge.get_gameobjects_info():
            print(e.game_object_name)
            if e.game_object_name == "MySphere":
                await _bridge.modify_game_object_scale(ScaleOperationDTO(instance_id=e.instance_id, target_scale=0.5))


@pytest.mark.asyncio
async def test_query_game_objects_info():
    async with TaskGroup() as tg:
        tg.create_task(test_conn())
        await syncwait()
        await create_sphere()
        await _bridge.query_update_gameobjects_info()
