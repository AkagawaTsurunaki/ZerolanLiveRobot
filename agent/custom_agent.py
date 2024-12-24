# See:
#   https://python.langchain.com/docs/tutorials/agents/
from injector import inject
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import BaseTool
from selenium.webdriver import Firefox, Chrome

from agent.tool.web_search import BaiduBaikeTool, MoeGirlTool
from agent.tool.go_creator import GameObjectCreator
from agent.tool_agent import ToolAgent
from common.config import LLMPipelineConfig
from services.viewer.app import ZerolanViewerServer


class CustomAgent:

    @inject
    def __init__(self, config: LLMPipelineConfig, driver: Firefox | Chrome, viewer: ZerolanViewerServer):
        self._model = ToolAgent(config=config)
        # Here to register more tools
        tools = [BaiduBaikeTool(), MoeGirlTool(driver), GameObjectCreator(viewer)]
        self._tools = {}
        self._model.bind_tools(tools)
        for tool in tools:
            self._tools[tool.name] = tool

    def run(self, query: str):
        messages = [self._model.system_prompt, HumanMessage(query)]
        ai_msg: AIMessage = self._model.invoke(messages)
        messages.append(ai_msg)
        for tool_call in ai_msg.tool_calls:
            tool_name = tool_call["name"].lower()
            selected_tool: BaseTool = self._tools.get(tool_name, None)
            if selected_tool is not None:
                tool_msg = selected_tool.invoke(tool_call)
                messages.append(tool_msg)
