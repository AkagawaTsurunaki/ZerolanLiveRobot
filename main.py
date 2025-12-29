import asyncio

from bot import ZerolanLiveRobot
from loguru import logger


async def main():
    try:
        bot = ZerolanLiveRobot()
        await bot.start()
        await bot.stop()
    except Exception as e:
        logger.exception(e)
        logger.error("❌️ Zerolan Live Robot exited abnormally!")


if __name__ == '__main__':
    asyncio.run(main())
