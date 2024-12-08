from typing import List

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from zerolan.data.pipeline.llm import Conversation

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

    def summary_history(self, history: List[Conversation]) -> AIMessage:
        system_template = "将这段用户与你的对话总结成一段话，需要包含重要细节。"
        text = ""
        for conversation in history:
            text += f"[{conversation.role}]\n{conversation.content}"
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{text}")]
        )
        result = prompt_template.invoke({"text": text})
        result.to_messages()
        response = self._model.invoke(result)

        return response
