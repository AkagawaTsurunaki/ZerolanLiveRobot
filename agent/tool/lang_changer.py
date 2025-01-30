from typing import Type, Any

from injector import inject
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from common.enumerator import Language
from main import ZerolanLiveRobot


class LangChangeInput(BaseModel):
    target_lang: Language = Field(description="Target language")


class LangChanger(BaseTool):
    name: str = "语言切换"
    description: str = "当用户需要切换语言时，使用此工具"
    args_schema: Type[BaseModel] = LangChangeInput
    return_direct: bool = True

    @inject
    def __init__(self, bot: ZerolanLiveRobot):
        super().__init__()
        self._bot = bot

    def _run(self, target_lang: Language) -> Any:
        if isinstance(target_lang, str):
            target_lang = Language.value_of(target_lang)
        self._bot.change_lang(target_lang)
