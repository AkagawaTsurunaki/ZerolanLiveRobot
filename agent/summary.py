from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate

from agent.adaptor import LangChainAdaptedLLM
from common.config import LLMPipelineConfig


class TextSummaryAgent:

    def __init__(self, config: LLMPipelineConfig):
        self._model: LangChainAdaptedLLM = LangChainAdaptedLLM(config=config)

    def summary(self, text: str, max_len: int = 100) -> AIMessage:
        """
        Summary the provided text within `max_len`.
        Args:
            text: The long text to summary.
            max_len: The maximum number of text of the summary.

        Returns:

        """
        system_template = "请仔细阅读文章内容，根据你认为最有价值和信息量的重要内容，总结这段文本为一段话。"

        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{text} \n任务：总结以上文本，不超过{max_len}字。")]
        )

        result = prompt_template.invoke({"text": text, "max_len": max_len})
        result.to_messages()
        response = self._model.invoke(result)

        return response
