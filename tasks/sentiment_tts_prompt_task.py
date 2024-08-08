from typing import List

from common.config.chara_config import TTSPrompt
from services.llm.pipeline import LLMPipeline
from tasks.llm.llm_sentiment_analyse_task import LLMSentimentAnalyseTask


class SentimentTtsPromptTask:
    def __init__(self, llm_pipeline: LLMPipeline, tts_prompts: List[TTSPrompt]):
        self._sentiment_ana_task = LLMSentimentAnalyseTask(llm_pipeline)
        self._tts_prompts = tts_prompts
        self._sentiments = [tts_prompt.sentiment for tts_prompt in tts_prompts]

    async def run(self, content: str) -> TTSPrompt:
        sentiment = await self._sentiment_ana_task.run(content=content, sentiments=self._sentiments)
        for tts_prompt in self._tts_prompts:
            if tts_prompt.sentiment == sentiment:
                return tts_prompt
        return self._tts_prompts[0]
