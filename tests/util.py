import asyncio
from asyncio import TaskGroup


async def syncwait(bridge):
    while not bridge.is_connected:
        await asyncio.sleep(0.1)


async def connect(bridge, auto_close_flag: bool = False):
    async with TaskGroup() as tg:
        start_task = tg.create_task(bridge.start())
        if auto_close_flag:
            await asyncio.sleep(2)
            print("Closing the WebSocket server")
            await bridge.stop()
            start_task.cancel()
