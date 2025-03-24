import typing
from typing import Optional, Any, Mapping, Sequence, Union, Callable

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.tools import BaseTool
from zerolan.data.pipeline.llm import LLMQuery, Conversation, RoleEnum
from ump.pipeline.llm import LLMPipeline, LLMPipelineConfig


def convert(messages: list[BaseMessage]) -> list[Conversation]:
    result = []
    for message in messages:
        result.append(convert_pipeline_query(message))
    return result


def convert_pipeline_query(message: BaseMessage):
    if isinstance(message, AIMessage):
        return Conversation(role=RoleEnum.assistant, content=message.content, metadata=None)
    elif isinstance(message, HumanMessage):
        return Conversation(role=RoleEnum.user, content=message.content, metadata=None)
    elif isinstance(message, SystemMessage):
        return Conversation(role=RoleEnum.system, content=message.content, metadata=None)
    elif isinstance(message, ToolMessage):
        return Conversation(role=RoleEnum.function, content=message.content, metadata=None)
    else:
        raise NotImplementedError(f"{type(message)} is not supported.")


class LangChainAdaptedLLM(BaseChatModel):
    """
    https://python.langchain.com/docs/how_to/custom_llm/
    """

    def _generate(self, messages: list[BaseMessage], stop: Optional[list[str]] = None,
                  run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any) -> ChatResult:
        # Replace this with actual logic to generate a response from a list
        # of messages.
        last_message = messages[-1]

        query = LLMQuery(text=last_message.content, history=convert(messages[0:-1]))
        prediction = self._pipeline.predict(query=query)

        content = prediction.response

        message = AIMessage(content=content)

        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def __init__(self, config: LLMPipelineConfig):
        super().__init__()
        self._tool_names = set[str]
        self._openai_tools: list[dict] = []
        self._pipeline = LLMPipeline(config=config)
        self._model_name = "CustomLLM"
        self._tools: Sequence[
            Union[typing.Dict[str, Any], type, Callable, BaseTool]  # noqa: UP006
        ] = []

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
            self,
            prompt: str,
            stop: Optional[list[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        prediction = self._pipeline.predict(LLMQuery(
            text=prompt,
            history=[]
        ))
        return prediction.response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model_name": self._model_name}
