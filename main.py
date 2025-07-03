import asyncio

from loguru import logger

from bot import ZerolanLiveRobot


async def main():
    try:
        bot = ZerolanLiveRobot()
        await bot.start()
    except Exception as e:
        logger.exception(e)
        logger.error("❌️ Zerolan Live Robot exited abnormally!")


if __name__ == '__main__':
    asyncio.run(main())
