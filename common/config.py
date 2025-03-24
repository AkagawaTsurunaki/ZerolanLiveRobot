from typing import Literal

from loguru import logger
from pydantic import BaseModel, Field
from zerolan.ump.pipeline.asr import ASRPipelineConfig
from zerolan.ump.pipeline.database import MilvusDatabaseConfig
from zerolan.ump.pipeline.img_cap import ImgCapPipelineConfig
from zerolan.ump.pipeline.llm import LLMPipelineConfig
from zerolan.ump.pipeline.ocr import OCRPipelineConfig
from zerolan.ump.pipeline.tts import TTSPipelineConfig
from zerolan.ump.pipeline.vid_cap import VidCapPipelineConfig
from zerolan.ump.pipeline.vla import ShowUIConfig

from common.utils.file_util import read_yaml, spath
from services.browser.config import BrowserConfig
from services.live_stream.config import LiveStreamConfig
from services.obs.config import ObsStudioClientConfig
from services.playground.config import PlaygroundBridgeConfig
from services.res.config import ResourceServerConfig


class VLAPipelineConfig(BaseModel):
    showui: ShowUIConfig
    enable: bool = True


class GameBridgeConfig(BaseModel):
    enable: bool = True
    host: str = '127.0.0.1'
    port: int = 11007
    platform: Literal["minecraft"] = "minecraft"


class QQBotBridgeConfig(BaseModel):
    enable: bool = True
    host: str = "0.0.0.0"
    port: int = 11014


class ServiceConfig(BaseModel):
    res_server: ResourceServerConfig
    live_stream: LiveStreamConfig
    game: GameBridgeConfig
    playground: PlaygroundBridgeConfig
    qqbot: QQBotBridgeConfig
    obs: ObsStudioClientConfig


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
    bot_name: str
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


class ExternalToolConfig(BaseModel):
    browser: BrowserConfig = Field(default=BrowserConfig(), description="Browser config")


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
