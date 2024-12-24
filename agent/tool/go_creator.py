import asyncio
from typing import Any, Type

from injector import inject
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from common.data import CreateGameObjectDTO
from services.viewer.app import ZerolanViewerServer


class GameObjectCreatorInput(BaseModel):
    dto: CreateGameObjectDTO = Field(description="DTO of the game object wiil be created")


class GameObjectCreator(BaseTool):
    name: str = "游戏对象创建器"
    description: str = "当用户要求你创建一个游戏对象（例如立方体、球体）的时候，使用此工具。"
    args_schema: Type[BaseModel] = GameObjectCreatorInput
    return_direct: bool = True

    @inject
    def __init__(self, viewer: ZerolanViewerServer):
        super().__init__()
        self._viewer = viewer

    def _run(self, dto: CreateGameObjectDTO) -> Any:
        task = asyncio.create_task(self._arun(dto))
        asyncio.wait([task])

    async def _arun(self, dto: CreateGameObjectDTO) -> None:
        await self._viewer.create_gameobject(dto)
