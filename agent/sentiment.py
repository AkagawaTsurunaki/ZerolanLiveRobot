from langchain_core.prompts import ChatPromptTemplate

from agent.adaptor import LangChainAdaptedLLM
from common.config import LLMPipelineConfig
from common.decorator import log_run_time
from manager.tts_prompt_manager import TTSPromptManager


class SentimentAnalyzerAgent:

    def __init__(self, manager: TTSPromptManager, config: LLMPipelineConfig):
        self._model: LangChainAdaptedLLM = LangChainAdaptedLLM(config=config)
        self._manager = manager
        self._sentiments: list[str] = self._manager.sentiments

    @log_run_time()
    def sentiment_analyse(self, text: str) -> str:

        if len(self._manager.tts_prompts) == 1:
            return self._manager.default_tts_prompt

        system_template = "你的任务：你现在是一个情感分析助手，你将要对所给的文句进行情感分析，你必须从以下情感标签中挑选一个作为答案 {sentiments}。\n输出格式：必须仅返回情感标签内容，不要输出多余内容。"

        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{text}")]
        )

        result = prompt_template.invoke({"sentiments": self._sentiments, "text": text})
        result.to_messages()
        response = self._model.invoke(result)
        # Try to parse the results of the LLM analysis
        #   1. If the sentiment tag is first matched in response, it is returned
        #   2. If the sentiment tag is not found, try to return the first match in ["normal", "正常", "default", "默认"]
        #   3. If the default/normal sentiment tag is not found, try returning the first sentiment tag
        for sentiment in self._sentiments:
            if sentiment in response.content:
                return sentiment
        for sentiment in self._sentiments:
            if "Default" in response.content:
                return sentiment
            elif "Normal" in response.content:
                return sentiment
            elif "默认" in response.content:
                return sentiment
            elif "正常" in response.content:
                return sentiment
        return self._sentiments[0]

    def sentiment_tts_prompt(self, text: str):
        sentiment = self.sentiment_analyse(text)
        return self._manager.get_tts_prompt(sentiment)
