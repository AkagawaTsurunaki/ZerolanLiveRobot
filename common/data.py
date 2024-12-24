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


class ViewerAction(str, Enum):
    CLIENT_HELLO = "client_hello"
    SERVER_HELLO = "server_hello"
    PLAY_SPEECH = "play_speech"
    LOAD_MODEL = "load_model"
    UPDATE_GAMEOBJECTS_INFO = "update_gameobjects_info"
    MODIFY_GAME_OBJECT_SCALE = "modify_gameobject_scale"


class FileInfo(BaseModel):
    file_id: str
    uri: str
    file_type: FileType
    origin_file_name: str
    file_name: str
    file_size: int  # Bytes
    sha256: str


class Position(BaseModel):
    x: float
    y: float
    z: float


class Transform(BaseModel):
    scale: float
    position: Position


class GameObjectInfo(BaseModel):
    instance_id: int
    game_object_name: str
    transform: Transform


class ScaleOperation(BaseModel):
    instance_id: int
    target_scale: float
