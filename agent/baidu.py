from typing import Type, Optional

import requests
from bs4 import BeautifulSoup
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.tools import BaseTool, ToolException
from loguru import logger
from pydantic import BaseModel, Field

from agent.summary import summary
from agent.tool_agent import ToolAgent
from common.config import get_config


def html_to_text_bs(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


# See:
#   https://python.langchain.com/docs/how_to/custom_tools/#subclassing-the-basetool-class


class BaiduBaikeToolInput(BaseModel):
    keyword: str = Field(description="The keyword you want to search.")


class BaiduBaikeTool(BaseTool):
    name: str = "百度百科"
    description: str = "Useful when you need search the information about specific concept."
    args_schema: Type[BaseModel] = BaiduBaikeToolInput
    return_direct: bool = True

    def __init__(self):
        super().__init__()

    def _run(self, keyword: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if isinstance(keyword, str) and keyword != "":
            response = requests.get(f"https://baike.baidu.com/item/{keyword}")
            html = response.content
            plain_text = html_to_text_bs(html)
            return plain_text
        else:
            raise ToolException("Keyword should not be empty")


# See:
#   https://python.langchain.com/docs/tutorials/agents/

def search_baike(query: str) -> BaseMessage:
    # Create the agent

    config = get_config()
    model = ToolAgent(config=config.pipeline.llm)
    baidubaike = BaiduBaikeTool()
    tools = [baidubaike]

    model.bind_tools(tools)

    messages = [model.system_prompt, HumanMessage(query)]
    ai_msg = model.invoke(messages)
    messages.append(ai_msg)
    for tool_call in ai_msg.tool_calls:
        selected_tool = {baidubaike.name: baidubaike}[tool_call["name"].lower()]
        tool_msg = selected_tool.invoke(tool_call)
        messages.append(tool_msg)

    logger.debug(messages)
    return messages[-1]

msg = search_baike("请搜素绫地宁宁")
summary(msg.content, "在游戏中，绫地宁宁变为魔女，但是代价是什么？")