import json
import typing
import uuid
from typing import Optional, Any, Mapping, Sequence, Union, Callable

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel, LanguageModelInput
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage, ToolCall
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from loguru import logger
from zerolan.data.data.llm import LLMQuery, Conversation, RoleEnum

from common.config import LLMPipelineConfig
from pipeline.llm import LLMPipeline


def convert(messages: list[BaseMessage]) -> list[Conversation]:
    result = []
    for message in messages:
        result.append(Conversation(message))
    return result


def convert_pipeline_query(message: BaseMessage):
    if isinstance(message, AIMessage):
        return Conversation(role=RoleEnum.system, content=message.content, metadata=None)
    elif isinstance(message, HumanMessage):
        return Conversation(role=RoleEnum.user, content=message.content, metadata=None)
    elif isinstance(message, SystemMessage):
        return Conversation(role=RoleEnum.system, content=message.content, metadata=None)
    else:
        raise NotImplementedError(f"{type(message)} is not supported.")


class LangChainAdaptedLLM(BaseChatModel):
    """
    https://python.langchain.com/docs/how_to/custom_llm/
    """

    def _parse_tool_call_intent(self, content: str) -> list[ToolCall] | None:
        try:
            tool_call = json.loads(content)
            if isinstance(tool_call, dict):
                try:
                    if tool_call["name"] in self._tool_names:
                        return [ToolCall(name=tool_call["name"], args=tool_call["args"], id=f'{uuid.uuid4()}')]
                except Exception as e:
                    return None
            elif isinstance(tool_call, list):
                result = []
                for call in tool_call:
                    try:
                        if call["name"] in self._tool_names:
                            result += [ToolCall(name=call["name"], args=call["args"], id=f'{uuid.uuid4()}')]
                    except Exception as e:
                        pass
                return None if result == [] else result
        except Exception:
            logger.warning("Seems like no tool call need.")

    def _generate(self, messages: list[BaseMessage], stop: Optional[list[str]] = None,
                  run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any) -> ChatResult:
        # Replace this with actual logic to generate a response from a list
        # of messages.
        last_message = messages[-1]

        query = LLMQuery(text=last_message.content, history=convert(messages[0:-2]))
        prediction = self._pipeline.predict(query=query)

        content = prediction.response

        tool_calls = self._parse_tool_call_intent(content)
        if tool_calls is None:
            message = AIMessage(content=content)
        else:
            message = AIMessage(content=content, tool_calls=tool_calls)

        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def bind_tools(
            self,
            tools: Sequence[
                Union[typing.Dict[str, Any], type, Callable, BaseTool]  # noqa: UP006
            ],
            **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        self._tools = tools
        self._openai_tools = [convert_to_openai_tool(tool) for tool in tools]
        self._tool_names = set([tool["function"]["name"] for tool in self._openai_tools])
        """
        [
            {
                "type": "function",
                "function": {
                    "name": "TOOL_NAME",
                    "description": "TOOL DESCRIPTION",
                    "parameters": {
                        "properties": {
                            "PROPERTY001": {
                                "description": "PROPERTY001_DESCRIPTION",
                                "type": "PROPERTY001_TYPE",
                            }
                        },
                        "required": [
                            "PROPERTY001"
                        ],
                        "type": "PARAMETERS_TYPE",
                    }
                }
            }
        ]
        """
        return self

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
