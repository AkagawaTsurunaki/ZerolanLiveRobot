import asyncio
import time

from loguru import logger

from services.game.minecraft.eventemitter import EventEmitter
from services.game.minecraft.data import Events


async def test_login():
    emitter = EventEmitter()

    @emitter.on(Events.login)
    async def print_something():
        logger.info("Bot login!")

    await emitter.emit(Events.login)

    logger.info("Finished")

async def test_chat():
    emitter = EventEmitter()

    @emitter.on(Events.chat)
    def chat(msg: str):
        logger.info("Bot chat: " + msg)

    time.sleep(1)

    await emitter.emit(Events.chat, msg="Hello!!")


asyncio.run(test_login())
asyncio.run(test_chat())