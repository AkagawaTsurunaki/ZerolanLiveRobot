from dataclasses import dataclass
from typing import Literal

from dataclasses_json import dataclass_json

from common.config.abs_config import AbstractConfigLoader
from common.register.model_register import ICModels, OCRModels, VidCapModels, TTSModels
from common.utils.file_util import read_yaml, spath


@dataclass
class ControllerConfig:
    host: str = "127.0.0.1"
    port: int = 11000


@dataclass
class ImgCapServiceConfig:
    # 是否启用本服务
    enable: bool = True
    # 服务地址
    host: str = '127.0.0.1'
    # 服务端口
    port: int = 11003
    # 模型 ID
    model_id: str = ICModels.BLIP_IMG_CAP_LARGE.id


@dataclass
class OCRServiceConfig:
    # 是否启用本服务
    enable: bool = True
    # 服务地址
    host: str = '127.0.0.1'
    # 服务端口
    port: int = 11004
    # 模型 ID
    model_id: str = OCRModels.PADDLE_OCR.id


@dataclass
class VidCapServiceConfig:
    # 是否启用本服务
    enable: bool = True
    # 服务地址
    host: str = '127.0.0.1'
    # 服务端口
    port: int = 11005
    # 模型 ID
    model_id: str = VidCapModels.HITEA_BASE.id


@dataclass
class TTSServiceConfig:
    # 是否启用本服务
    enable: bool = True
    # 服务地址
    host: str = '127.0.0.1'
    # 服务端口
    port: int = 11006
    # 模型 ID
    model_id: str = TTSModels.GPT_SOVITS.id


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
    # asr_config: ASRServiceConfig | None = None
    # llm_config: LLMServiceConfig | None = None
    ocr_config: OCRServiceConfig | None = None
    imgcap_config: ImgCapServiceConfig | None = None
    controller_config: ControllerConfig | None = None
    vidcap_config: VidCapServiceConfig | None = None
    tts_config: TTSServiceConfig | None = None
    live_stream_config: LiveStreamServiceConfig | None = None
    game_config: GameServiceConfig | None = None


class Loader(AbstractConfigLoader):
    @staticmethod
    def load_config():
        config_data = read_yaml(spath("resources/config/services_config.yaml"))
        # ServiceConfig.asr_config = ASRServiceConfig(**config_data.get('ASRServiceConfig', {}))
        # ServiceConfig.llm_config = LLMServiceConfig(**config_data.get('LLMServiceConfig', {}))
        ServiceConfig.imgcap_config = ImgCapServiceConfig(**config_data.get('ImgCapServiceConfig', {}))
        ServiceConfig.ocr_config = OCRServiceConfig(**config_data.get('OCRServiceConfig', {}))
        ServiceConfig.controller_config = ControllerConfig(**config_data.get('ControllerConfig', {}))
        ServiceConfig.vidcap_config = VidCapServiceConfig(**config_data.get('VidCapServiceConfig', {}))
        ServiceConfig.tts_config = TTSServiceConfig(**config_data.get('TTSServiceConfig', {}))
        ServiceConfig.live_stream_config = LiveStreamServiceConfig.from_dict(  # type: ignore
            config_data.get(LiveStreamServiceConfig.__name__, {})
        )
        ServiceConfig.game_config = GameServiceConfig.from_dict(  # type: ignore
            config_data.get(GameServiceConfig.__name__, {})
        )


Loader.load_config()
