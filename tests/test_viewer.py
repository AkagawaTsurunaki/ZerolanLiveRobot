import asyncio
from asyncio import TaskGroup

from agent.api import model_scale
from services.viewer.app import ZerolanViewerServer

viewer = ZerolanViewerServer(host="0.0.0.0", port=11013, protocol="ZerolanViewerProtocol", version="1.0")


async def run():
    async with TaskGroup() as tg:
        tg.create_task(viewer.start())

        while not viewer.is_connected:
            await asyncio.sleep(1)

        await asyncio.sleep(1)
        print("准备获取")
        info = viewer.get_gameobjects_info()
        s = model_scale(info, "请把UnityChan的模型放大两倍")
        print(s)
        await viewer.modify_game_object_scale(s)


def test_model_scale():
    asyncio.run(run())
