import asyncio
import threading
import time

from langchain_core.messages import ToolCall

from services.game.minecraft.app import KonekoMinecraftAIAgent
from services.game.minecraft.data import KonekoProtocol

ws = KonekoMinecraftAIAgent(host="127.0.0.1", port=10098)


async def test_ws():
    ws_thr = threading.Thread(target=ws.start)
    ws_thr.start()
    # ws.start()

    while True:
        time.sleep(1)
        protocolObj = KonekoProtocol(data=ToolCall(name="chat", args={"content": "Ciallo!"}, id="144"),
                                     type="instruction")
        await ws.send_message(protocolObj)
        print("Send")

    # t.join()
    ws_thr.join()


asyncio.run(test_ws())
