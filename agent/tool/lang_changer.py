from typing import Type, Any

from injector import inject
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from common.enumerator import Language
from common.utils.enum_util import enum_members_to_list
from event.event_data import LanguageChangeEvent
from event.event_emitter import emitter


class LangChangeInput(BaseModel):
    target_lang: str = Field(description=f"Target language: {enum_members_to_list(Language)}, Only return ")


class LangChanger(BaseTool):
    name: str = "语言切换"
    description: str = "当用户需要切换语言时，使用此工具"
    args_schema: Type[BaseModel] = LangChangeInput
    return_direct: bool = True

    @inject
    def __init__(self):
        super().__init__()

    def _run(self, target_lang: Language) -> Any:
        if isinstance(target_lang, str):
            target_lang = Language.value_of(target_lang)
        emitter.emit(LanguageChangeEvent(target_lang=target_lang))
