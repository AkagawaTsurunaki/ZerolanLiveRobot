import os.path
from enum import Enum

from zerolan.data.protocol.protocol import ZerolanProtocol

from common.data import PlaySpeechDTO, LoadLive2DModelDTO, FileInfo, ScaleOperationDTO, CreateGameObjectDTO, \
    GameObjectInfo
from common.utils.audio_util import check_audio_format, check_audio_info
from common.utils.collection_util import to_value_list
from common.utils.file_util import path_to_uri
from services.playground.bridge import PlaygroundBridge


class Action(str, Enum):
    PLAY_SPEECH = "play_speech"
    LOAD_LIVE2D_MODEL = "load_live2d_model"

    CLIENT_HELLO = "client_hello"
    SERVER_HELLO = "server_hello"

    LOAD_3D_MODEL = "load_model"
    UPDATE_GAMEOBJECTS_INFO = "update_gameobjects_info"
    MODIFY_GAMEOBJECT_SCALE = "modify_gameobject_scale"
    CREATE_GAMEOBJECT = "create_gameobject"


_bridge = PlaygroundBridge(host="0.0.0.0", port=11013)


def is_playground_connected():
    def decorator(func):
        if _bridge.is_connected:
            return func()
        else:
            raise RuntimeError("未建立连接，操作无效")

    return decorator


async def send(action: str, data: any, msg: str = None, code: int = 0):
    zp = ZerolanProtocol(protocol="ZerolanProtocol", version="1.0",
                         message=msg, code=code,
                         action=action, data=data)
    await _bridge.send(zp)


@is_playground_connected()
async def play_speech(bot_id: str, audio_path: str, transcript: str):
    audio_type = check_audio_format(audio_path)
    sample_rate, num_channels, duration = check_audio_info(audio_path)
    audio_uri = path_to_uri(audio_path)
    await send(action=Action.PLAY_SPEECH, data=PlaySpeechDTO(bot_id=bot_id, audio_uri=audio_uri,
                                                             transcript=transcript,
                                                             audio_type=audio_type,
                                                             sample_rate=sample_rate,
                                                             channels=num_channels,
                                                             duration=duration))


@is_playground_connected()
async def load_live2d_model(bot_id: str, bot_display_name: str, model_dir: str):
    assert os.path.exists(model_dir) and os.path.isdir(model_dir), f"{model_dir} is not a directory 或不存在"
    await send(action=Action.LOAD_LIVE2D_MODEL, data=LoadLive2DModelDTO(bot_id=bot_id,
                                                                        bot_display_name=bot_display_name,
                                                                        model_dir=model_dir))


@is_playground_connected()
async def load_3d_model(file_info: FileInfo):
    """
    从 Model Manager 处可以得到 FileInfo
    Args:
        file_info: FileInfo 实例
    """
    await send(action=Action.LOAD_3D_MODEL,
               data=file_info)


@is_playground_connected()
async def modify_game_object_scale(dto: ScaleOperationDTO):
    await send(action=Action.MODIFY_GAMEOBJECT_SCALE, data=dto)


@is_playground_connected()
async def create_gameobject(dto: CreateGameObjectDTO):
    await send(action=Action.CREATE_GAMEOBJECT, data=dto)


@is_playground_connected()
async def query_update_gameobjects_info():
    await send(action=Action.UPDATE_GAMEOBJECTS_INFO, data=None)


@is_playground_connected()
def get_gameobjects_info() -> list[GameObjectInfo]:
    return to_value_list(_bridge.gameobjects_info)
