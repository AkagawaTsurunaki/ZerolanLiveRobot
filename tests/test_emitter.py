import asyncio
import time

from loguru import logger

from common.eventemitter import emitter


async def test_login():
    @emitter.on("service.game.login")
    async def print_something():
        logger.info("Bot login!")

    await emitter.emit("service.game.login")

    logger.info("Finished")


async def test_chat():
    @emitter.on("service.game.chat")
    def chat(msg: str):
        logger.info("Bot chat: " + msg)

    time.sleep(1)

    await emitter.emit("service.game.chat", msg="Hello!!")


asyncio.run(test_login())
asyncio.run(test_chat())
