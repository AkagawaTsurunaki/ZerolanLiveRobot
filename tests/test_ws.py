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
    # tool = agent._instructions[0]
    # config = get_config()
    # model = ToolAgent(config=config.pipeline.llm)
    # tools = [tool]
    #
    # model.bind_tools(tools)
    # messages = [model.system_prompt, HumanMessage("我要与大家聊天，跟大家说：你好！这里是一则通知")]
    # ai_msg: AIMessage = model.invoke(messages)
    # messages.append(ai_msg)
    # for tool_call in ai_msg.tool_calls:
    #     selected_tool: BaseTool = tool
    #     tool_msg = selected_tool.invoke(tool_call)
    #     messages.append(tool_msg)
    # print(messages)
    # tool.invoke(ToolCall(id="asdsad", args={"content": "Ciallo"}, name="chat"))


    ws_thr.join()


test_ws()
