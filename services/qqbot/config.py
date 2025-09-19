from typing import List
from pydantic import BaseModel, Field


class QQBotServiceConfig(BaseModel):
    enable: bool = Field(True, description="Whether to enable the QQBotBridge.")
    qq_num: int = Field(-1, description="QQ number.")
    ws_uri: str = Field("ws://127.0.0.1:3033", description="Uri of websocket connected to NapCat.")
    ws_token: str = Field("", description="Token for this websocket server.")
    groups: List[int] = Field([], description="Chat groups.")
    friends: List[int] = Field([], description="Chat friends.")
    root: int = Field(-1, description="Root user.")