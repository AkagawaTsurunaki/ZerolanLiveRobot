import threading

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import BaseTool

from agent.tool_agent import Tool, Function, Parameters, Property, ToolAgent
from common.config import get_config
from services.game.minecraft.app import KonekoMinecraftAIAgent, WebSocketServer

ws = WebSocketServer()
agent = KonekoMinecraftAIAgent(ws)


def test_ws():
    ws_thr = threading.Thread(target=agent.start)
    ws_thr.start()

    # l = [
    #     Tool(type="function",
    #          function=Function(name="chat", description="asasd",
    #                            parameters=Parameters(
    #                                properties={"content": Property(description="用于与大家聊天", type="string"),
    #                                            # "time": Property(description="asasd", type="number"),
    #                                            },
    #                                required=["content"],
    #                                type="ChatInstruction")))
    # ]



    ws_thr.join()


test_ws()


