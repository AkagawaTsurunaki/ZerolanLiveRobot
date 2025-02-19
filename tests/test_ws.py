from asyncio import TaskGroup

import pytest
from loguru import logger

from event.websocket import WebSocketServer


@pytest.mark.asyncio
async def test_ws():
    ws = WebSocketServer('127.0.0.1', 11013, match_sub_protocol="ZerolanProtocol")
    async with TaskGroup() as tg:
        tg.create_task(ws.start())
    logger.info("Test passed")
