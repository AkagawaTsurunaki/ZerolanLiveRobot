import asyncio
import uuid
from typing import Type

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

    def _run(self, **kwargs) -> str:
        return asyncio.run(self._arun(**kwargs))

    async def _arun(self, **kwargs) -> str:
        tool_call = ToolCall(id=f"{uuid.uuid4()}", name=self.name, args=kwargs)
        protocol_obj = KonekoProtocol(event=EventEnum.KONEKO_SERVER_CALL_INSTRUCTION, data=tool_call)
        await emitter.emit(EventEnum.KONEKO_SERVER_CALL_INSTRUCTION, protocol_obj=protocol_obj)
        return f"Instruction {self.name} executed"
