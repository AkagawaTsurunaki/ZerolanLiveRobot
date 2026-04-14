from pydantic import BaseModel, Field
from zerolan.pipeline.asr.config import ASRPipelineConfig
from zerolan.pipeline.imgcap.config import ImgCapPipelineConfig
from zerolan.pipeline.llm.config import LLMPipelineConfig
from zerolan.pipeline.ocr.config import OCRPipelineConfig
from zerolan.pipeline.tts.config import TTSPipelineConfig
from zerolan.pipeline.vidcap.config import VidCapPipelineConfig
from zerolan.pipeline.vla.showui.config import ShowUIPipelineConfig

from pipeline.db.milvus.config import VectorDBConfig


class ASRConfig(ASRPipelineConfig):
    enable: bool = Field(default=True, description="Enable the Automatic Speech Recognition pipeline.")


class LLMConfig(LLMPipelineConfig):
    enable: bool = Field(default=True, description="Enable the Large Language Model pipeline.")


class ImgCapConfig(ImgCapPipelineConfig):
    enable: bool = Field(default=True, description="Enable the Image Captioning pipeline.")


class OCRConfig(OCRPipelineConfig):
    enable: bool = Field(default=True, description="Enable the Optical Character Recognition pipeline.")


class VidCapConfig(VidCapPipelineConfig):
    enable: bool = Field(default=True, description="Enable the Video Captioning pipeline.")


class TTSConfig(TTSPipelineConfig):
    enable: bool = Field(default=True, description="Enable the Text-to-Speech pipeline.")


class ShowUIConfig(ShowUIPipelineConfig):
    enable: bool = Field(default=True, description="Enable the ShowUI pipeline.")


class VLAConfig(BaseModel):
    showui: ShowUIConfig = Field(default=ShowUIPipelineConfig(), description="Configuration for the ShowUI pipeline.")


class VecDBConfig(VectorDBConfig):
    enable: bool = Field(default=True, description="Enable the Vector Database.")


class PipelineConfig(BaseModel):
    asr: ASRConfig = Field(default=ASRConfig(),
                           description="Configuration for the Automatic Speech Recognition pipeline.")
    llm: LLMConfig = Field(default=LLMConfig(),
                           description="Configuration for the Large Language Model pipeline.")
    img_cap: ImgCapConfig = Field(default=ImgCapConfig(),
                                  description="Configuration for the Image Captioning pipeline.")
    ocr: OCRConfig = Field(default=OCRConfig(),
                           description="Configuration for the Optical Character Recognition pipeline.")
    vid_cap: VidCapConfig = Field(default=VidCapConfig(),
                                  description="Configuration for the Video Captioning pipeline.")
    tts: TTSConfig = Field(default=TTSConfig(),
                           description="Configuration for the Text-to-Speech pipeline.")
    vla: VLAConfig = Field(default=VLAConfig(),
                           description="Configuration for the Visual Language Action pipeline.")
    vec_db: VecDBConfig = Field(default=VecDBConfig(),
                                description="Configuration for the Vector Database.")
