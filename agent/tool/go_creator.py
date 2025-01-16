import asyncio
from typing import Any, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from common.data import CreateGameObjectDTO
from services.playground.api import create_gameobject


class GameObjectCreatorInput(BaseModel):
    dto: CreateGameObjectDTO = Field(description="DTO of the game object will be created")


class GameObjectCreator(BaseTool):
    name: str = "游戏对象创建器"
    description: str = "当用户要求你创建一个游戏对象（例如立方体、球体）的时候，使用此工具。"
    args_schema: Type[BaseModel] = GameObjectCreatorInput
    return_direct: bool = True

    def __init__(self):
        super().__init__()

    def _run(self, dto: CreateGameObjectDTO) -> Any:
        task = [asyncio.create_task(self._arun(dto))]
        asyncio.gather(*task)

    async def _arun(self, dto: CreateGameObjectDTO) -> None:
        await create_gameobject(dto)
