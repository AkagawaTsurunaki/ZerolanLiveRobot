from typing import Literal

from loguru import logger
from pydantic import BaseModel
from zerolan.ump.pipeline.asr import ASRPipelineConfig
from zerolan.ump.pipeline.database import MilvusDatabaseConfig
from zerolan.ump.pipeline.img_cap import ImgCapPipelineConfig
from zerolan.ump.pipeline.llm import LLMPipelineConfig
from zerolan.ump.pipeline.ocr import OCRPipelineConfig
from zerolan.ump.pipeline.tts import TTSPipelineConfig
from zerolan.ump.pipeline.vid_cap import VidCapPipelineConfig
from zerolan.ump.pipeline.vla import ShowUIConfig

from common.utils.file_util import read_yaml, spath


class VLAPipelineConfig(BaseModel):
    showui: ShowUIConfig
    enable: bool = True


class ControllerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 11000


class BilibiliServiceConfig(BaseModel):
    class Credential(BaseModel):
        sessdata: str = ""
        bili_jct: str = ""
        buvid3: str = ""

    room_id: int = -1
    credential: Credential = ""


class TwitchServiceConfig(BaseModel):
    channel_id: str = ""
    app_id: str = ""
    app_secret: str | None = None


class YoutubeServiceConfig(BaseModel):
    # GCloud auth print access token
    token: str = ""


class LiveStreamConfig(BaseModel):
    enable: bool = True
    bilibili: BilibiliServiceConfig = None
    twitch: TwitchServiceConfig = None
    youtube: YoutubeServiceConfig = None


class Live2DConfig(BaseModel):
    enable: bool = True
    host: str = "127.0.0.1"
    port: int = 11008
    model_dir: str = "resources/static/models/live2d/"


class GameBridgeConfig(BaseModel):
    enable: bool = True
    host: str = '127.0.0.1'
    port: int = 11007
    platform: Literal["minecraft"] = "minecraft"


class ZerolanViewerConfig(BaseModel):
    enable: bool = True
    host: str = '0.0.0.0'
    port: int = 11013


class ServiceConfig(BaseModel):
    controller: ControllerConfig
    live_stream: LiveStreamConfig
    game: GameBridgeConfig
    live2d: Live2DConfig
    viewer: ZerolanViewerConfig


class FilterConfig(BaseModel):
    bad_words: list[str]
    strategy: Literal["default"] = "default"


class ChatConfig(BaseModel):
    filter: FilterConfig
    system_prompt: str
    injected_history: list[str]
    max_history: int = 20


class SpeechConfig(BaseModel):
    prompts_dir: str = "resources/static/prompts/tts"


class CharacterConfig(BaseModel):
    chat: ChatConfig
    speech: SpeechConfig


class VectorDBConfig(BaseModel):
    enable: bool = True
    milvus: MilvusDatabaseConfig | None = None


class PipelineConfig(BaseModel):
    asr: ASRPipelineConfig
    llm: LLMPipelineConfig
    img_cap: ImgCapPipelineConfig
    ocr: OCRPipelineConfig
    vid_cap: VidCapPipelineConfig
    tts: TTSPipelineConfig
    vla: VLAPipelineConfig
    vec_db: VectorDBConfig


class BrowserConfig(BaseModel):
    enable: bool = True
    profile_dir: str | None = None
    driver: Literal["chrome", "firefox"] = "firefox"


class ExternalToolConfig(BaseModel):
    browser: BrowserConfig


class ZerolanLiveRobotConfig(BaseModel):
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
    config = ZerolanLiveRobotConfig.model_validate(cfg_dict)
    return config
