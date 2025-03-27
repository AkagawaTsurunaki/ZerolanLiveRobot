"""
API documents will be generated from here.
"""

from enum import Enum

from pydantic import BaseModel, Field

from common.utils.enum_util import enum_members_to_list


class PlaySpeechRequest(BaseModel):
    bot_id: str = Field(description="The unique identifier of the bot.")
    bot_display_name: str = Field(description="The display name of the bot.")
    audio_download_endpoint: str = Field(description="The endpoint of the audio file to be played. \n"
                                                     "Note: Need to combine with something like `http://127.0.0.1`")
    transcript: str = Field(description="The text transcript of the audio.")
    audio_type: str = Field(description="The type of the audio. \n"
                                        "Supported: wav, ogg.")
    sample_rate: int = Field(description="The sample rate of the audio in Hz.")
    channels: int = Field(description="The number of audio channels (e.g., 1 for mono, 2 for stereo).")
    duration: float = Field(description="The duration of the audio in seconds.")


class LoadLive2DModelRequest(BaseModel):
    bot_id: str = Field(description="The unique identifier of the bot.")
    bot_display_name: str = Field(description="The display name of the bot.")
    model_download_endpoint: str = Field(description="The endpoint of the Live2D model file. \n"
                                                     "Note: Need to combine with something like `http://127.0.0.1`")


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


class GameObject(BaseModel):
    instance_id: int
    game_object_name: str
    transform: Transform


class ScaleOperationRequest(BaseModel):
    instance_id: int
    target_scale: float


class BuiltinGameObjectType(str, Enum):
    CUBE = "cube"
    SPHERE = "sphere"


class CreateGameObjectRequest(BaseModel):
    instance_id: int = Field(description="The id of the gameobject instance")
    game_object_name: str = Field(description="The name of the gameobject")
    object_type: BuiltinGameObjectType = Field(
        description=f"The type of the gameobject, can be only in {enum_members_to_list(BuiltinGameObjectType)}")
    color: str = Field(description='The color of the gameobject, hex format: "#000000"')
    transform: Transform = Field(description="The transform of the gameobject")


class ShowUserTextInputRequest(BaseModel):
    text: str = Field(description="The text input (transcript from ASR) from the user that needs to be shown.")


class ServerHello(BaseModel):
    server_ipv6: str = Field(description="The IPv6 address of the ZerolanPlayground WebSocket server.")
    server_ipv4: str = Field(description="The IPv4 address of the ZerolanPlayground WebSocket server.")
    server_ws_port: int = Field(description="The port number of the ZerolanPlayground WebSocket server.")
    server_grpc_port: int = Field(description="The port number of the gRPC server.")
    server_res_port: int = Field(description="The resource port number of the Resource HTTP server.")


class AddChatHistory(BaseModel):
    role: str = Field(description="The role associated with the history entry. \n"
                                  "`user`: User text from ASR. \n"
                                  "`assistant`: Assistant text from LLM. \n"
                                  "`system`: System info, warning, error, etc. \n")
    text: str = Field(description="The text content of the chat message.")
    username: str = Field(description="The username of the user who created the chat message.")
