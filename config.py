from pydantic import BaseModel, Field
from zerolan.pipeline.asr.config import ASRPipelineConfig
from zerolan.pipeline.db.milvus.config import MilvusPipelineConfig
from zerolan.pipeline.imgcap.config import ImgCapPipelineConfig
from zerolan.pipeline.llm.config import LLMPipelineConfig
from zerolan.pipeline.ocr.config import OCRPipelineConfig
from zerolan.pipeline.tts.config import TTSPipelineConfig
from zerolan.pipeline.vidcap.config import VidCapPipelineConfig
from zerolan.pipeline.vla.showui.config import ShowUIPipelineConfig

from character.config import CharacterConfig
from common.utils.enum_util import try_get_pynput_key_enum_str
from services.config import ServiceConfig


class VLAPipelineConfig:
    showui = Field(default=ShowUIPipelineConfig(), description="Configuration for the ShowUI pipeline.")


class VectorDBConfig(BaseModel):
    milvus: MilvusPipelineConfig = Field(default=MilvusPipelineConfig(),
                                         description="Configuration for the Milvus Database pipeline.")


class PipelineConfig(BaseModel):
    asr: ASRPipelineConfig = Field(default=ASRPipelineConfig(),
                                   description="Configuration for the Automatic Speech Recognition pipeline.")
    llm: LLMPipelineConfig = Field(default=LLMPipelineConfig(),
                                   description="Configuration for the Large Language Model pipeline.")
    img_cap: ImgCapPipelineConfig = Field(default=ImgCapPipelineConfig(),
                                          description="Configuration for the Image Captioning pipeline.")
    ocr: OCRPipelineConfig = Field(default=OCRPipelineConfig(),
                                   description="Configuration for the Optical Character Recognition pipeline.")
    vid_cap: VidCapPipelineConfig = Field(default=VidCapPipelineConfig(),
                                          description="Configuration for the Video Captioning pipeline.")
    tts: TTSPipelineConfig = Field(default=TTSPipelineConfig(),
                                   description="Configuration for the Text-to-Speech pipeline.")
    vla: VLAPipelineConfig = Field(default=VLAPipelineConfig(),
                                   description="Configuration for the Visual Language Action pipeline.")
    vec_db: VectorDBConfig = Field(default=VectorDBConfig(), description="Configuration for the Vector Database.")


class SystemConfig(BaseModel):
    default_enable_microphone: bool = Field(default=False,
                                            description="For safety, do not open your microphone by default. \n"
                                                        "You can set it `True` to enable your microphone")
    microphone_vad_mode: int = Field(default=3,
                                     description="Optionally, set its aggressiveness mode, which is an integer between 0 and 3. " \
                                                 "0 is the least aggressive about filtering out non-speech, 3 is the most aggressive.")
    microphone_hotkey: str = Field(default='f8',
                                   description="Your microphone is set to be off when the program starts. One tap on this hotkey will change its status between on and off.\n" \
                                               "You can pick your own hotkey on Key names like: {} ...".format(
                                       try_get_pynput_key_enum_str()))
    enable_clause_split: bool = Field(default=True,
                                      description='If `True`, splits LLM responses into smaller clauses before sending to TTS service. '
                                                  'This enables faster audio generation and reduced latency for real-time applications. \n'
                                                  'Set to `False` to send full sentences as a single unit for more natural speech flow at the cost of longer wait times.')
    enable_sentiment_analysis: bool = Field(default=False,
                                            description='Automatically analyzes sentiment to select appropriate TTS prompts. '
                                                        'This also increases token consumption and adds slight latency due to extra processing.')
    enable_intelligent_memory: bool = Field(default=False,
                                            description='🧪 EXPERIMENTAL: Automatically scores and filters conversation history entries based on sentiment, relevance, and safety.')


class ZerolanLiveRobotConfig(BaseModel):
    pipeline: PipelineConfig = Field(default=PipelineConfig(),
                                     description="Configuration for the pipeline settings. \n"
                                                 "The pipeline is the key to connecting to `ZerolanCore`, \n"
                                                 "which typically accesses the model via HTTP or HTTPS requests and gets a response from the model. \n"
                                                 "> [!NOTE] \n"
                                                 "> 1. At a minimum, you need to enable the LLMPipeline. \n"
                                                 "> 2. ZerolanCore is distributed, and you can deploy different models to different servers. Just set different url to connect to your models. \n"
                                                 "> 3. If your server can only open one port, try forwarding your network requests using [Nginx](https://nginx.org/en/).")
    service: ServiceConfig = Field(default=ServiceConfig(),
                                   description="Configuration for the service settings. \n"
                                               "The services are usually opened locally, \n"
                                               "and instances of other projects establish WebSocket or HTTP connections with the service, \n"
                                               "and the service controls the behavior of its sub-project instances.")
    character: CharacterConfig = Field(default=CharacterConfig(),
                                       description="Configuration for the character settings.")
    system: SystemConfig = Field(default=SystemConfig(), description="Configuration for the system settings.")
