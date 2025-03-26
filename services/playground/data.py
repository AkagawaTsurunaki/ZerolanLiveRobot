from enum import Enum

from pydantic import BaseModel


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


class ShowUserTextInputDTO(BaseModel):
    text: str


class ServerHello(BaseModel):
    server_ipv6: str
    server_ipv4: str
    server_ws_port: int = 11000
    server_grpc_port: int = 8443


class AddHistoryDTO(BaseModel):
    role: str
    text: str
    username: str
