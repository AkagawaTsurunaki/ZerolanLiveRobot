from typing import Type, Optional

import requests
from bs4 import BeautifulSoup
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool, ToolException
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from agent.adaptor import LangChainAdaptedLLM
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
    description: str = "Useful when you need search the information about specific concept, works like Wikipedia."
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

# Create the agent
config = get_config()
model = LangChainAdaptedLLM(config=config.pipeline.llm)
memory = MemorySaver()
baidubaike = BaiduBaikeTool()
tools = [baidubaike]

agent_executor = create_react_agent(model, tools, checkpointer=memory)
agent_config = {"configurable": {"thread_id": "abc123"}}
for chunk in agent_executor.stream(
        {"messages": [
            HumanMessage(content="你现在是一个有用的AI Agent，你可以使用的工具有\n"
                                  + str(model._openai_tools)
                                  + "\n你只能输出JSON内容，遵循严格的JSON格式！你的输出JSON格式类似如下的格式，请注意匹配工具名和参数："
                                  + str({"name": "ToolName", "args": {"tool_arg1": "value1"}})
                                  + "现在根据工具和用户输入，返回JSON格式的输出以调用其他工具. 现在帮助我在百科上搜索 绫地宁宁"),
            # HumanMessage(content="Help me search 绫地宁宁")
        ]}, config=agent_config
):
    print(chunk)
    print("---")
