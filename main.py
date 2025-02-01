import asyncio

from bot import ZerolanLiveRobot


async def main():
    bot = ZerolanLiveRobot()
    await bot.start()
    bot.exit()


if __name__ == '__main__':
    asyncio.run(main())
