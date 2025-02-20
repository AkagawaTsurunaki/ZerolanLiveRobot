import asyncio
import time
from dataclasses import dataclass

from loguru import logger

from event.event_data import BaseEvent
from event.eventemitter import emitter
from event.registry import EventKeyRegistry


@dataclass
class TestEvent(BaseEvent):
    content: str
    type = EventKeyRegistry.Dev.TEST


@emitter.on(EventKeyRegistry.Dev.TEST)
def exit__(event: TestEvent):
    print("To sleep!")
    time.sleep(2)
    print(f"time: {event.content}")


@emitter.on(EventKeyRegistry.Dev.TEST)
async def aexit(event: TestEvent):
    print("To sleep!")
    await asyncio.sleep(2)
    print(f"time: {event.content}")


async def main():
    task = asyncio.create_task(emitter.start())

    await asyncio.sleep(1)

    emitter.emit(TestEvent(content="Hello!"))

    await asyncio.sleep(3)
    logger.info("Emitter stop!")
    await emitter.stop()

    await task
    # await emitter.stop()


def test_event_emitter():
    asyncio.run(main())
