import asyncio

from bot import ZerolanLiveRobot
from loguru import logger

from common.concurrent.abs_runnable import stop_all_runnable


async def main():
    try:
        bot = ZerolanLiveRobot()
        await bot.start()
        bot.stop()
    except Exception as e:
        logger.exception(e)
        logger.error("❌️ Zerolan Live Robot exited abnormally!")


if __name__ == '__main__':
    asyncio.run(main())
