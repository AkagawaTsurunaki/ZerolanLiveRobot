import asyncio
import time
from random import random

from loguru import logger

from event.event_data import SleepEvent, EventType
from event.eventemitter import emitter


@emitter.on(EventType.EXIT)
def exit__(event: SleepEvent):
    print("To sleep!")
    time.sleep(2)
    print(f"time: {event.sleep_time}")


@emitter.on(EventType.EXIT)
async def aexit(event: SleepEvent):
    print("To sleep!")
    await asyncio.sleep(event.sleep_time)
    print(f"time: {event.sleep_time}")


async def main():
    task = asyncio.create_task(emitter.start())

    await asyncio.sleep(1)

    emitter.emit(SleepEvent(sleep_time=random() * 100))

    await asyncio.sleep(3)
    logger.info("Emitter stop!")
    await emitter.stop()

    await task
    # await emitter.stop()


def test_event_emitter():
    asyncio.run(main())
