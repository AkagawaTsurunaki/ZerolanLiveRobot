import asyncio
import time
from asyncio import TaskGroup
from dataclasses import dataclass

import aiohttp
import pytest

from event.event_data import BaseEvent
from event.event_emitter import emitter


class TestEvent(BaseEvent):
    content: str
    type = "test.run_forever"


@dataclass
class ConnTest(BaseEvent):
    content: str
    type = "test.conn"


@emitter.on("test.run_forever")
async def some_task(event: TestEvent):
    i = 0
    while True:
        await asyncio.sleep(1)
        print(f"Async: {i} {event.content}")
        i += 1


@emitter.on("test.conn")
async def connections(event: ConnTest):
    async with aiohttp.ClientSession(base_url="http://127.0.0.1") as session:
        async with TaskGroup() as tg:
            tg.create_task(session.get("/asdasd"))
            tg.create_task(session.get("/asdasd"))
            tg.create_task(session.get("/asdasd"))
            tg.create_task(session.get("/asdasd"))
            tg.create_task(session.get("/asdasd"))
            tg.create_task(session.get("/asdasd"))
            tg.create_task(session.get("/asdasd"))
            print(event.content)


@emitter.on("test.run_forever")
def some_sync_task(event: TestEvent):
    i = 0
    while True:
        time.sleep(0.5)
        print(f"Sync: {i} {event.content}")
        i += 1


@emitter.on("test.conn")
async def run_once(_):
    print("You should see this content only once!")


@pytest.mark.asyncio
async def test_event_emitter():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(emitter.start())
        emitter.emit("test.conn", ConnTest(content="Ciallo"))
        emitter.emit("test.run_forever", ConnTest(content="Ciallo"))
        await asyncio.sleep(1)
        await emitter.stop()
