import asyncio

from loguru import logger

from event.websocket import WebSocketServer


async def main():
    ws = WebSocketServer('127.0.0.1', 8111)
    ws_task = asyncio.create_task(ws.start())
    await asyncio.sleep(4)
    await ws.send_json({"test": "1"})
    logger.info("Sent message")
    await asyncio.sleep(0.5)
    await ws.stop()

    await ws_task
    logger.info("Test passed")


def test_ws():
    asyncio.run(main())
