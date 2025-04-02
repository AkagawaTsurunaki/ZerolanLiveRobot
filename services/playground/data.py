"""
API documents will be generated from here.

We define that:
    Request is the data object send from client to server.
    Response is the data object send from server to client.
This is not defined by who is the sender or who is the receiver, please note.
"""
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from common.utils.enum_util import enum_members_to_list


class PlaySpeechResponse(BaseModel):
    bot_id: str = Field(description="The unique identifier of the bot.")
    bot_display_name: str = Field(description="The display name of the bot.")
    file_id: str = Field(description="The endpoint of the audio file to be played. \n"
                                                     "Note: Need to combine with something like `http://127.0.0.1`")
    transcript: str = Field(description="The text transcript of the audio.")
    audio_type: str = Field(description="The type of the audio. \n"
                                        "Supported: wav, ogg.")
    sample_rate: int = Field(description="The sample rate of the audio in Hz.")
    channels: int = Field(description="The number of audio channels (e.g., 1 for mono, 2 for stereo).")
    duration: float = Field(description="The duration of the audio in seconds.")


class LoadLive2DModelResponse(BaseModel):
    bot_id: str = Field(description="The unique identifier of the bot.")
    bot_display_name: str = Field(description="The display name of the bot.")
    model_file_id: str = Field(description="The endpoint of the Live2D model file. \n"
                                                     "Note: Need to combine with something like `http://127.0.0.1`")


class FileType(str, Enum):
    ZIP = "zip"
    GLB = "glb"
    GLTF = "gltf"
    FBX = "fbx"
    NONE = "none"


class FileInfo(BaseModel):
    file_id: str = Field(description="The unique identifier of the file.")
    uri: str = Field(description="The URI of the file.")
    file_type: FileType = Field(description="The type of the file (e.g., image, video, audio, document).")
    origin_file_name: str = Field(description="The original name of the file when it was uploaded.")
    file_name: str = Field(description="The current name of the file after processing or storage.")
    file_size: int = Field(description="The size of the file in bytes.")


class Position(BaseModel):
    x: float = Field(description="x position")
    y: float = Field(description="y position")
    z: float = Field(description="z position")


class Transform(BaseModel):
    scale: float = Field(description="The scale of the gameobject")
    position: Position = Field(description="The position of the gameobject")


class GameObject(BaseModel):
    instance_id: int = Field(description="The unique identifier of the game object instance.")
    game_object_name: str = Field(description="The name of the game object.")
    transform: Transform = Field(description="The transformation data (position, rotation, scale) of the game object.")


class ScaleOperationResponse(BaseModel):
    instance_id: int = Field(description="The unique identifier of the game object instance that was scaled.")
    target_scale: float = Field(description="The target scale value applied to the game object.")


class BuiltinGameObjectType(str, Enum):
    CUBE = "cube"
    SPHERE = "sphere"


class CreateGameObjectResponse(BaseModel):
    instance_id: int = Field(description="The id of the gameobject instance")
    game_object_name: str = Field(description="The name of the gameobject")
    object_type: BuiltinGameObjectType = Field(
        description=f"The type of the gameobject, can be only in {enum_members_to_list(BuiltinGameObjectType)}")
    color: str = Field(description='The color of the gameobject, hex format: "#000000"')
    transform: Transform = Field(description="The transform of the gameobject")


class ShowUserTextInputResponse(BaseModel):
    text: str = Field(description="The text input (transcript from ASR) from the user that needs to be shown.")


class ServerHello(BaseModel):
    ws_domain_or_ip: str = Field(
        description="The domain name or the IP address of the ZerolanPlayground WebSocket server.")
    ws_port: int = Field(description="The port number of the ZerolanPlayground WebSocket server.")
    res_domain_or_ip: str = Field(
        description="The domain name or the IP address of the Resource HTTP server."
    )
    res_port: int = Field(description="The resource port number of the Resource HTTP server.")


class AddChatHistory(BaseModel):
    role: str = Field(description="The role associated with the history entry. \n"
                                  "`user`: User text from ASR. \n"
                                  "`assistant`: Assistant text from LLM. \n"
                                  "`system`: System info, warning, error, etc. \n")
    text: str = Field(description="The text content of the chat message.")
    username: str = Field(description="The username of the user who created the chat message.")


class SelectionItem(BaseModel):
    id: int = Field(description="The unique identifier of the selection item.")
    interactive: bool = Field(description="Whether the selection item is interactive or not.")
    text: str = Field(description="The content of the selection item.")
    img_id: str | None = Field(None, description="The ID of the image of the selection item.")


class ShowTopMenu(BaseModel):
    uuid: str = Field(description="The unique identifier of the selection group.")
    items: List[SelectionItem] = Field(description="The selection group. Contains all selection items.")
    destroy_last: bool = Field(default=True,
                               description="Whether the last selection group should be destroyed before the current one is shown.")


class Arg_MenuItem(BaseModel):
    img_path: str | None
    text: str | None
    interactive: bool = True
