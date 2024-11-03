from dataclasses import dataclass
from typing import Literal

from dataclasses_json import dataclass_json

from common.config.abs_config import AbstractConfigLoader
from common.utils.file_util import read_yaml, spath


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
class LiveStreamServiceConfig:
    enable: bool = True
    platform: Literal["bilibili"] = "bilibili"
    room_id: str = None
    credential: BiliCredential = None


@dataclass_json
@dataclass
class GameServiceConfig:
    enable: bool = True
    # 服务地址
    host: str = '127.0.0.1'
    # 服务端口
    port: int = 11007
    platform: Literal["minecraft"] = "minecraft"


class ServiceConfig:
    controller_config: ControllerConfig | None = None
    live_stream_config: LiveStreamServiceConfig | None = None
    game_config: GameServiceConfig | None = None


class Loader(AbstractConfigLoader):
    @staticmethod
    def load_config():
        config_data = read_yaml(spath("resources/config/services_config.yaml"))

        ServiceConfig.live_stream_config = LiveStreamServiceConfig.from_dict(  # type: ignore
            config_data.get(LiveStreamServiceConfig.__name__, {})
        )
        ServiceConfig.game_config = GameServiceConfig.from_dict(  # type: ignore
            config_data.get(GameServiceConfig.__name__, {})
        )


Loader.load_config()
