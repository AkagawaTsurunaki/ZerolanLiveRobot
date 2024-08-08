from common.enum.lang import Language
from services.llm.pipeline import LLMPipeline, LLMQuery
from loguru import logger

from tasks.llm.prompt import ICIOPrompt


class LLMTranslateTask:
    def __init__(self, llm_pipeline: LLMPipeline = None):
        self._pipeline: LLMPipeline = LLMPipeline() if llm_pipeline is None else llm_pipeline

    async def run(self, content: str, from_lang: Language, to_lang: Language):
        assert content is not None, f"Empty content."
        assert from_lang != to_lang, f"Source language is same as target language: {from_lang}."
        sys_prompt = ICIOPrompt(
            instruction=f"你将要对所给的文段进行翻译，从{from_lang.to_zh_name()}到{to_lang.to_zh_name()}。",
            input_data=content,
            output_indicator="必须仅返回翻译内容，不要输出其他内容。"
        )
        query = LLMQuery(text=sys_prompt.en_format(), history=[])
        prediction = self._pipeline.predict(query)
        logger.info(f"翻译任务结果: {prediction.response}")
        return prediction.response
