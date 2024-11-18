import asyncio
from typing import Type, Any

from langchain_core.messages import ToolCall
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from common.enumerator import EventEnum
from common.eventemitter import emitter
from services.game.minecraft.data import KonekoProtocol


class KonekoInstructionTool(BaseTool):
    name: str = None
    description: str = None
    args_schema: Type[BaseModel] = None
    return_direct: bool = True

    def __init__(self, name: str, description: str, args_schema: Type[BaseModel]) -> None:
        super().__init__()
        self.name = name
        self.description = description
        self.args_schema = args_schema

    def _run(self, tool_call: ToolCall) -> Any:
        asyncio.gather(asyncio.create_task(self._arun(tool_call)))

    async def _arun(self, tool_call: ToolCall) -> Any:
        protocol_obj = KonekoProtocol(event=EventEnum.KONEKO_SERVER_CALL_INSTRUCTION, data=tool_call)
        await emitter.emit(EventEnum.KONEKO_SERVER_CALL_INSTRUCTION, protocol_obj)
