from enum import Enum

from pydantic import BaseModel


class PlaySpeechDTO(BaseModel):
    bot_id: str
    audio_uri: str
    transcript: str
    audio_type: str
    sample_rate: int
    channels: int
    duration: float


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
    sha256: str
