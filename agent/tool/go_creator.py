import asyncio
from typing import Any, Type

from injector import inject
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from services.playground.data import CreateGameObjectResponse
from services.playground.bridge import PlaygroundBridge


class GameObjectCreatorInput(BaseModel):
    dto: CreateGameObjectResponse = Field(description="DTO of the game object will be created")


class GameObjectCreator(BaseTool):
    name: str = "游戏对象创建器"
    description: str = "当用户要求你创建一个游戏对象（例如立方体、球体）的时候，使用此工具。"
    args_schema: Type[BaseModel] = GameObjectCreatorInput
    return_direct: bool = True

    @inject
    def __init__(self, bridge: PlaygroundBridge):
        super().__init__()
        self._bridge = bridge

    def _run(self, dto: CreateGameObjectResponse) -> Any:
        task = [asyncio.create_task(self._arun(dto))]
        asyncio.gather(*task)

    async def _arun(self, dto: CreateGameObjectResponse) -> None:
        await self._bridge.create_gameobject(dto)
