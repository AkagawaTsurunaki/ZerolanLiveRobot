from common.utils.enum_util import enum_to_markdown_zh
from services.browser.config import SeleniumDriverEnum

__markdown_doc__ = f"""
基于 Selenium 的简单的浏览器控制器。{enum_to_markdown_zh(SeleniumDriverEnum)}
功能很简单，如果需要扩展需要自己实现。其中机器人可能会使用 ShowUI 的模型推理结果来调用并控制浏览器。
""".strip()
