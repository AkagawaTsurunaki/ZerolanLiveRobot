from pydantic import BaseModel, Field
from zerolan.ump.pipeline.asr import ASRPipelineConfig
from zerolan.ump.pipeline.database import MilvusDatabaseConfig
from zerolan.ump.pipeline.img_cap import ImgCapPipelineConfig
from zerolan.ump.pipeline.llm import LLMPipelineConfig
from zerolan.ump.pipeline.ocr import OCRPipelineConfig
from zerolan.ump.pipeline.tts import TTSPipelineConfig
from zerolan.ump.pipeline.vid_cap import VidCapPipelineConfig
from zerolan.ump.pipeline.vla import ShowUIConfig


class VLAPipelineConfig(BaseModel):
    showui: ShowUIConfig = Field(default=ShowUIConfig(), description="Configuration for the ShowUI component.")
    enable: bool = Field(default=True, description="Whether the Visual Language Action pipeline is enabled.")


class VectorDBConfig(BaseModel):
    enable: bool = Field(default=True, description="Whether the Vector Database is enabled.")
    milvus: MilvusDatabaseConfig = Field(default=MilvusDatabaseConfig(),
                                         description="Configuration for the Milvus Database.")


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
