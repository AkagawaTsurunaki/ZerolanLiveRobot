from typing import Type, Optional

import requests
from bs4 import BeautifulSoup
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool, ToolException
from loguru import logger
from pydantic import BaseModel, Field
from selenium.webdriver import Firefox, Chrome


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
            content = html_to_text(html)
            if "百度百科错误页" in content:
                raise ToolException(f"BaiduBaike returns error page: {keyword} is not found?")
            return content
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
        except Exception as _:
            pass
        plain_text = html_to_text(self._driver.page_source)
        return plain_text
