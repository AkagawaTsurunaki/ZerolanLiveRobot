from enum import Enum

from pydantic import BaseModel, Field

from common.utils.enum_util import enum_members_to_list


class PlaySpeechDTO(BaseModel):
    bot_id: str
    bot_display_name: str
    audio_uri: str
    transcript: str
    audio_type: str
    sample_rate: int
    channels: int
    duration: float


class LoadLive2DModelDTO(BaseModel):
    bot_id: str
    bot_display_name: str
    model_dir: str
    model_uri: str


class FileType(str, Enum):
    ZIP = "zip"
    GLB = "glb"
    GLTF = "gltf"
    FBX = "fbx"
    NONE = "none"


class FileInfo(BaseModel):
    file_id: str
    uri: str
    file_type: FileType
    origin_file_name: str
    file_name: str
    file_size: int  # Bytes


class Position(BaseModel):
    x: float = Field(description="x position")
    y: float = Field(description="y position")
    z: float = Field(description="z position")


class Transform(BaseModel):
    scale: float = Field(description="The scale of the gameobject")
    position: Position = Field(description="The position of the gameobject")


class GameObjectInfo(BaseModel):
    instance_id: int
    game_object_name: str
    transform: Transform


class ScaleOperationDTO(BaseModel):
    instance_id: int
    target_scale: float


class GameObjectType(str, Enum):
    CUBE = "cube"
    SPHERE = "sphere"


class CreateGameObjectDTO(BaseModel):
    instance_id: int = Field(description="The id of the gameobject instance")
    game_object_name: str = Field(description="The name of the gameobject")
    object_type: GameObjectType = Field(
        description=f"The type of the gameobject, can be only in {enum_members_to_list(GameObjectType)}")
    color: str = Field(description='The color of the gameobject, hex format: "#000000"')
    transform: Transform = Field(description="The transform of the gameobject")


class ShowUserTextInputDTO(BaseModel):
    text: str


class ServerHello(BaseModel):
    grpc_server_url: str
