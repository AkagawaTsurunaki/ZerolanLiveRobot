from loguru import logger
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
class BilibiliServiceConfig:
    @dataclass_json
    @dataclass
    class Credential:
        sessdata: str = ""
        bili_jct: str = ""
        buvid3: str = ""

    room_id: int = -1
    credential: Credential = ""


@dataclass_json
@dataclass
class TwitchServiceConfig:
    channel_id: str = ""
    app_id: str = ""
    app_secret: str | None = None


@dataclass_json
@dataclass
class YoutubeServiceConfig:
    # GCloud auth print access token
    token: str = ""


@dataclass_json
@dataclass
class LiveStreamConfig:
    enable: bool = True
    bilibili: BilibiliServiceConfig = None
    twitch: TwitchServiceConfig = None
    youtube: YoutubeServiceConfig = None


@dataclass_json
@dataclass
class Live2DConfig:
    enable: bool = True
    host: str = "127.0.0.1"
    port: int = 11008
    model_dir: str = "resources/static/models/live2d/"


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
    live2d: Live2DConfig


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
class BrowserConfig:
    enable: bool = True
    profile_dir: str | None = None
    driver: Literal["chrome", "firefox"] = "firefox"


@dataclass_json
@dataclass
class ExternalToolConfig:
    browser: BrowserConfig


@dataclass_json
@dataclass
class ZerolanLiveRobotConfig:
    pipeline: PipelineConfig
    service: ServiceConfig
    character: CharacterConfig
    external_tool: ExternalToolConfig


def get_config() -> ZerolanLiveRobotConfig:
    try:
        cfg_dict = read_yaml(spath("resources/config.yaml"))
    except Exception as e:
        logger.error("Are you sure that you have copied `config.yaml` from `config.template.yaml` in `resources`?`")
        raise e

    assert hasattr(ZerolanLiveRobotConfig, "from_dict")
    config: ZerolanLiveRobotConfig = ZerolanLiveRobotConfig.from_dict(cfg_dict)  # noqa
    return config
