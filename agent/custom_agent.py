# See:
#   https://python.langchain.com/docs/tutorials/agents/
from injector import inject
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import BaseTool
from loguru import logger
from selenium.webdriver import Firefox, Chrome

from agent.tool.go_creator import GameObjectCreator
from agent.tool.lang_changer import LangChanger
from agent.tool.microphone_tool import MicrophoneTool
from agent.tool.web_search import BaiduBaikeTool, MoeGirlTool
from agent.tool_agent import ToolAgent
from services.playground.bridge import PlaygroundBridge
from ump.pipeline.llm import LLMPipelineConfig


class CustomAgent:

    @inject
    def __init__(self, config: LLMPipelineConfig, driver: Firefox | Chrome = None,
                 bridge: PlaygroundBridge | None = None):
        self._model = ToolAgent(config=config)
        # Here to register more tools
        tools = [BaiduBaikeTool(), LangChanger(), MicrophoneTool()]
        if driver is not None:
            tools.append(MoeGirlTool(driver))
        if bridge is not None:
            tools.append(GameObjectCreator())
        self._tools = {}
        self._model.bind_tools(tools)
        for tool in tools:
            self._tools[tool.name] = tool

    def run(self, query: str) -> bool:
        messages = [self._model.system_prompt, HumanMessage(query)]
        ai_msg: AIMessage = self._model.invoke(messages)
        messages.append(ai_msg)
        if len(ai_msg.tool_calls) == 0:
            logger.debug("No tool to call in this conversation")
            return False
        for tool_call in ai_msg.tool_calls:
            tool_name = tool_call["name"].lower()
            selected_tool: BaseTool = self._tools.get(tool_name, None)
            if selected_tool is not None:
                try:
                    tool_msg = selected_tool.invoke(tool_call)
                    messages.append(tool_msg)
                except Exception as e:
                    logger.warning(e)
                    pass

        return True
