import asyncio
import time

from services.game.minecraft.app import KonekoMinecraftAIAgent
from services.game.minecraft.data import KonekoProtocol

ws = KonekoMinecraftAIAgent(host="127.0.0.1", port=10098)


async def test_ws():
    # t = threading.Thread(target=ws.start)
    # t.start()
    ws_thr = ws.start()

    while True:
        time.sleep(1)
        await ws.send_message(KonekoProtocol(data={"command": "chat", "message": "Hello!"}))

    # t.join()
    ws_thr.join()

asyncio.run(test_ws())
