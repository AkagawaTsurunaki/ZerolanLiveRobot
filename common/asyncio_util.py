import asyncio
from typing import Coroutine


def sync_wait(coro: Coroutine):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(coro)
    return result
