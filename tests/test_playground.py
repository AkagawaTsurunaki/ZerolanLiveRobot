import asyncio
import time
from asyncio import TaskGroup

import pytest

from config import get_config
from common.data import LoadLive2DModelDTO, CreateGameObjectDTO, GameObjectType, Transform, Position, ScaleOperationDTO
from common.concurrent.killable_thread import KillableThread
from manager.model_manager import ModelManager
from services.playground.bridge import PlaygroundBridge
from util import syncwait, connect

_config = get_config()
_bridge = PlaygroundBridge(_config.service.playground)

auto_close_flag = False

_bridge_thread = KillableThread(target=_bridge.start, daemon=True)


def wait_conn():
    while not _bridge.is_connected:
        time.sleep(0.1)


def block_forever():
    while True:
        time.sleep(0.1)


def test_conn():
    _bridge_thread.start()
    wait_conn()
    _bridge.stop()
    _bridge_thread.join()
    print("Test passed")


# You should put at least 1 3D-model file under `../resources/static/models/3d`,
# Or the test case will not work.
# You can also change the path if you want.
def test_load_3d_model():
    _bridge_thread.start()
    _manager = ModelManager("../resources/static/models/3d")
    _manager.scan()
    file_id = _manager.get_files()[0]["id"]
    file_info = _manager.get_file_by_id(file_id)
    wait_conn()

    time.sleep(3)
    _bridge.load_3d_model(file_info)
    block_forever()
    _bridge.stop()
    _bridge_thread.join()


# You should set Live2D-model file path in your config.yaml
# Or the test case will not work.
def test_load_live2d_model():
    _bridge_thread.start()
    model_dir = _config.service.playground.model_dir
    bot_id = _config.service.playground.bot_id
    bot_name = _config.character.bot_name
    wait_conn()
    _bridge.load_live2d_model(LoadLive2DModelDTO(bot_id=bot_id, model_dir=model_dir, bot_display_name=bot_name))
    block_forever()


async def create_sphere():
    await _bridge.create_gameobject(
        CreateGameObjectDTO(instance_id=114, game_object_name="MySphere", object_type=GameObjectType.SPHERE,
                            color="#114514", transform=Transform(scale=5.0, position=Position(x=1, y=1, z=1))))


@pytest.mark.asyncio
async def test_create_gameobject():
    async with TaskGroup() as tg:
        tg.create_task(connect(_bridge, auto_close_flag))
        await syncwait(_bridge)
        await create_sphere()


@pytest.mark.asyncio
async def test_modify_game_object_scale():
    async with TaskGroup() as tg:
        tg.create_task(connect(_bridge, auto_close_flag))
        await syncwait(_bridge)
        await create_sphere()
        await asyncio.sleep(1)
        for e in _bridge.get_gameobjects_info():
            print(e.game_object_name)
            if e.game_object_name == "MySphere":
                await _bridge.modify_game_object_scale(ScaleOperationDTO(instance_id=e.instance_id, target_scale=0.5))


@pytest.mark.asyncio
async def test_query_game_objects_info():
    async with TaskGroup() as tg:
        tg.create_task(connect(_bridge, auto_close_flag))
        await syncwait(_bridge)
        await create_sphere()
        await _bridge.query_update_gameobjects_info()
