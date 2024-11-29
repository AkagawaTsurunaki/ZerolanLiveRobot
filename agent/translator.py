from langchain_core.prompts import ChatPromptTemplate

from agent.adaptor import LangChainAdaptedLLM
from common.config import LLMPipelineConfig
from common.enumerator import Language


class TranslatorAgent:

    def __init__(self, config: LLMPipelineConfig):
        self._model = LangChainAdaptedLLM(config=config)

    def translate(self, text: str, src_lang: str | Language, tgt_lang: str | Language) -> str:

        if isinstance(src_lang, Language):
            src_lang = src_lang.name()
        if isinstance(tgt_lang, Language):
            tgt_lang = tgt_lang.name()

        system_template = "Translate the following from {src_lang} into {tgt_lang}"

        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{text}")]
        )

        result = prompt_template.invoke({"src_lang": src_lang, "tgt_lang": tgt_lang, "text": text})
        result.to_messages()
        response = self._model.invoke(result)

        return response.content
