from pydantic import BaseModel, Field


class QQBotBridgeConfig(BaseModel):
    enable: bool = Field(True, description="Whether to enable the QQBotBridge.")
    host: str = Field("0.0.0.0", description="The host address of the QQBotBridge service.")
    port: int = Field(11014, description="The port number of the QQBotBridge service.")
