from enum import unique

from pydantic import BaseModel, Field

from common.enumerator import BaseEnum


@unique
class PlatformEnum(BaseEnum):
    Minecraft: str = "minecraft"


class GameBridgeConfig(BaseModel):
    enable: bool = Field(True, description="Whether to enable the GameBridge.")
    host: str = Field("127.0.0.1", description="The host address of the GameBridge service.")
    port: int = Field(11007, description="The port number of the GameBridge service.")
    platform: PlatformEnum = Field(PlatformEnum.Minecraft,
                                   description="The platform type, currently only supports `minecraft`.")
