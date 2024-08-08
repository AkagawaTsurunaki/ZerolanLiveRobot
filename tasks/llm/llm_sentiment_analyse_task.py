from typing import List

from loguru import logger

from services.llm.pipeline import LLMPipeline, LLMQuery
from tasks.llm.prompt import ICIOPrompt


class LLMSentimentAnalyseTask:
    def __init__(self, llm_pipeline: LLMPipeline):
        self._pipeline = llm_pipeline if llm_pipeline is not None else LLMPipeline()

    async def run(self, content: str, sentiments: List[str]) -> str:
        assert content is not None, f"Empty content."
        assert sentiments is not None and len(sentiments) != 0, f"Empty sentiments."
        sentiments_str = ""
        for sentiment in sentiments:
            sentiments_str += f"{sentiment}\n"
        sys_prompt = ICIOPrompt(
            instruction=f"你将要对所给的文段进行情感分析，你必须从以下 {len(sentiments)} 个情感标签中挑选一个作为答案 ```\n {sentiments_str} \n```",
            input_data=content,
            output_indicator="必须仅返回情感标签内容，不要输出多余内容。"
        )
        query = LLMQuery(text=sys_prompt.en_format(), history=[])
        prediction = self._pipeline.predict(query)
        logger.info(f"情感分析任务结果: {prediction.response}")
        # 尝试解析 LLM 分析的结果
        #   1. 如果包含了情感标签那么直接返回
        #   2. 如果无法找到情感标签, 那么尝试返回 ["正常", "normal", "默认", "default"] 中的首个匹配项
        #   3. 如果仍无法找到, 那么尝试返回第一个情感标签
        for sentiment in sentiments:
            if sentiment in prediction.response:
                return sentiment
        for sentiment in sentiments:
            for default_sentiment in ["正常", "normal", "默认", "default"]:
                if default_sentiment in prediction.response:
                    return sentiment
        return sentiments[0]
