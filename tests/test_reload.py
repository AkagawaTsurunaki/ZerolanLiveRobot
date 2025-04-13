import asyncio
from asyncio import TaskGroup

import pytest

from bot import BaseBot
from manager.config_manager import get_config


@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    # Needed to work with asyncpg
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_reload_pipelines():
    bot = BaseBot()
    async with TaskGroup() as tg:
        tg.create_task(bot.start())
        await asyncio.sleep(1)
        bot.reload_pipeline()
        await asyncio.sleep(1)
        config = get_config()
        config.pipeline.asr.predict_url = "http://127.0.0.1/asr/predict"
        bot.reload_pipeline()
        await bot.stop()


@pytest.mark.asyncio
async def test_reload_device():
    bot = BaseBot()
    async with TaskGroup() as tg:
        tg.create_task(bot.start())
        await asyncio.sleep(1)
        bot.reload_device()
        await asyncio.sleep(1)
        config = get_config()
        config.system.default_enable_microphone = not config.system.default_enable_microphone
        bot.reload_device()
        await bot.stop()
