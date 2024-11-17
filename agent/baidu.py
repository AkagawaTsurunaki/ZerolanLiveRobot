from typing import Type, Optional

import requests
from bs4 import BeautifulSoup
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool, ToolException
from loguru import logger
from pydantic import BaseModel, Field
from selenium.webdriver import Firefox, Chrome

from agent.tool_agent import ToolAgent
from common.config import get_config


def html_to_text(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


def get_html(url: str):
    response = requests.get(url)
    html = response.content
    return html


# See:
#   https://python.langchain.com/docs/how_to/custom_tools/#subclassing-the-basetool-class


class BaiduBaikeToolInput(BaseModel):
    keyword: str = Field(description="The keyword you want to search.")


class BaiduBaikeTool(BaseTool):
    name: str = "百度百科"
    description: str = "当你需要搜索某个专业的知识点、概念的时候，使用此工具。"
    args_schema: Type[BaseModel] = BaiduBaikeToolInput
    return_direct: bool = True

    def __init__(self):
        """
        Get page content from
        """
        super().__init__()
        self._url = "https://baike.baidu.com/item"

    def _run(self, keyword: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if isinstance(keyword, str) and keyword != "":
            html = get_html(f"{self._url}/{keyword}")
            return html_to_text(html)
        else:
            raise ToolException("Keyword should not be empty")


class MoeGirlTool(BaseTool):
    name: str = "萌娘百科"
    description: str = "当你需要搜索二次元人物、游戏、漫画等资料时，使用此工具。"

    def __init__(self, driver: Firefox | Chrome):
        """
        Get page content from MoeGirl (萌娘百科).
        Args:
            driver:
        """
        super().__init__()
        self._url = "https://mzh.moegirl.org.cn"
        self._driver: Firefox | Chrome = driver

    def _run(self, keyword: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        self._driver.set_page_load_timeout(5)
        try:
            self._driver.get(f"{self._url}/{keyword}")
            for i in range(3):
                self._driver.execute_script("window.scrollBy(0,3000)")
                logger.debug(f"Scroll by 3000 * {i}")
            self._driver.implicitly_wait(1)
        except Exception as e:
            pass
        plain_text = html_to_text(self._driver.page_source)
        return plain_text


# See:
#   https://python.langchain.com/docs/tutorials/agents/

def search_baike(query: str) -> str:
    """
    Parse the keyword from the query and search for it on BaiduBaike.
    This will use `requests` to GET the target website and remove the HTML tag in source HTML file.
    Args:
        query: Plain text query.

    Returns: The plain text result in Baike

    """
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
    return messages[-1].content
