import json
import re
import typing
import uuid
from json import JSONDecodeError
from typing import Optional, Any, Sequence, Union, Callable

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, ToolCall
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from loguru import logger
from pydantic import BaseModel
from zerolan.data.data.llm import LLMQuery

from agent.adaptor import LangChainAdaptedLLM, convert
from common.config import LLMPipelineConfig


class Property(BaseModel):
    description: str
    type: str


class Parameters(BaseModel):
    properties: dict[str, Property]
    required: list[str]
    type: str


class Function(BaseModel):
    name: str
    description: str
    parameters: Parameters


class Tool(BaseModel):
    type: str
    function: Function


class ToolAgent(LangChainAdaptedLLM):
    def __init__(self, config: LLMPipelineConfig):
        super().__init__(config)

    def _parse_tool_call_intent(self, content: str) -> list[ToolCall] | None:
        try:
            content = extract_json_from_markdown(content)
            try:
                tool_call = json.loads(content)
            except JSONDecodeError:
                content = remove_extra_braces(content)
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

        query = LLMQuery(text=last_message.content, history=convert(messages[0:-1]))
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

    @property
    def system_prompt(self):
        return SystemMessage(content="你现在是一个有用的AI Agent，你可以使用的工具有\n"
                                     + json.dumps(self._openai_tools, ensure_ascii=False)
                                     + "\n你的输出JSON格式类似如下的格式，请注意匹配工具名和参数："
                                     + json.dumps({"name": "ToolName", "args": {"tool_arg1": "value1"}},
                                                  ensure_ascii=False)
                                     + "现在根据工具和用户输入，返回JSON格式的输出以调用其他工具。你只能输出JSON内容，不要带Markdown，并检查你的大括号，遵循严格的JSON格式！")


def extract_json_from_markdown(markdown_text: str) -> str:
    cleaned_text = re.sub(r'```.*?\n(.*?)\n```', r'\1', markdown_text, flags=re.DOTALL)
    return cleaned_text


def remove_extra_braces(json_string):
    for i in range(len(json_string) - 1, 0, -1):
        print(i)
        if json_string[i] == '}':
            json_string = json_string[:i] + json_string[i + 1:]
            return json_string
