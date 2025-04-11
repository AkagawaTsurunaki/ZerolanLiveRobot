from asyncio import TaskGroup

import pytest

from config import get_config
from services.qqbot.bridge import QQBotBridge
from util import connect, syncwait

_config = get_config()
_bridge = QQBotBridge(_config.service.qqbot)

auto_close_flag = False


# You can test the connection to ZerolanPlayground
# All test cases will depend on this function so make sure you test it at first.
@pytest.mark.asyncio
async def test_conn():
    async with TaskGroup() as tg:
        tg.create_task(connect(_bridge, auto_close_flag))
        await syncwait(_bridge)
