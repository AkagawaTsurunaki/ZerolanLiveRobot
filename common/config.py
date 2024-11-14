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


@dataclass_json
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
    host: str = '127.0.0.1'
    port: int = 11007
    platform: Literal["minecraft"] = "minecraft"


@dataclass_json
@dataclass
class ServiceConfig:
    controller: ControllerConfig
    live_stream: LiveStreamConfig
    game: GameBridgeConfig


@dataclass_json
@dataclass
class FilterConfig:
    bad_words: list[str]
    strategy: Literal["default"] = "default"


@dataclass_json
@dataclass
class ChatConfig:
    filter: FilterConfig
    system_prompt: str
    injected_history: list[str]
    max_history: int = 20


@dataclass_json
@dataclass
class SpeechConfig:
    prompts_dir: str = "resources/static/prompts/tts"


@dataclass_json
@dataclass
class CharacterConfig:
    chat: ChatConfig
    speech: SpeechConfig


@dataclass_json
@dataclass
class PipelineConfig:
    asr: ASRPipelineConfig
    llm: LLMPipelineConfig
    img_cap: ImgCapPipelineConfig
    ocr: OCRPipelineConfig
    vid_cap: VidCapPipelineConfig
    tts: TTSPipelineConfig


@dataclass_json
@dataclass
class ZerolanLiveRobotConfig:
    pipeline: PipelineConfig
    service: ServiceConfig
    character: CharacterConfig


def get_config() -> ZerolanLiveRobotConfig:
    cfg_dict = read_yaml(spath("resources/config.yaml"))
    assert hasattr(ZerolanLiveRobotConfig, "from_dict")
    config: ZerolanLiveRobotConfig = ZerolanLiveRobotConfig.from_dict(cfg_dict)  # noqa
    return config
