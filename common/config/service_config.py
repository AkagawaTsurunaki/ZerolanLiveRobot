from dataclasses import dataclass
from typing import Literal

from dataclasses_json import dataclass_json

from common.utils.file_util import read_yaml, spath

@dataclass_json
@dataclass
class ASRPipelineConfig:
    enable: bool = True
    server_url: str = "http://127.0.0.1:11001"
    sample_rate: int = 16000
    channels: int = 1
    format: Literal["float32"] = "float32"

@dataclass_json
@dataclass
class LLMPipelineConfig:
    enable: bool = True
    server_url: str = "http://127.0.0.1:11002"

@dataclass_json
@dataclass
class ImgCapPipelineConfig:
    enable: bool = True
    server_url: str = "http://127.0.0.1:11003"

@dataclass_json
@dataclass
class OCRPipelineConfig:
    enable: bool = True
    server_url: str = "http://127.0.0.1:11004"

@dataclass_json
@dataclass
class VidCapPipelineConfig:
    enable: bool = True
    server_url: str = "http://127.0.0.1:11005"

@dataclass_json
@dataclass
class TTSPipelineConfig:
    enable: bool = True
    server_url: str = "http://127.0.0.1:11006"

@dataclass
class ControllerConfig:
    host: str = "127.0.0.1"
    port: int = 11000


@dataclass_json
@dataclass
class BiliCredential:
    sessdata: str = None
    bili_jct: str = None
    buvid3: str = None


@dataclass_json
@dataclass
class LiveStreamConfig:
    enable: bool = True
    platform: Literal["bilibili"] = "bilibili"
    room_id: str = None
    credential: BiliCredential = None


@dataclass_json
@dataclass
class GameBridgeConfig:
    enable: bool = True
    # 服务地址
    host: str = '127.0.0.1'
    # 服务端口
    port: int = 11007
    platform: Literal["minecraft"] = "minecraft"


class ServiceConfig:
    controller_config: ControllerConfig | None = None
    live_stream_config: LiveStreamConfig | None = None
    game_config: GameBridgeConfig | None = None


class Loader:
    @staticmethod
    def load_config():
        config_data = read_yaml(spath("resources/config/services_config.yaml"))

        ServiceConfig.live_stream_config = LiveStreamConfig.from_dict(  # type: ignore
            config_data.get(LiveStreamConfig.__name__, {})
        )
        ServiceConfig.game_config = GameBridgeConfig.from_dict(  # type: ignore
            config_data.get(GameBridgeConfig.__name__, {})
        )


Loader.load_config()
