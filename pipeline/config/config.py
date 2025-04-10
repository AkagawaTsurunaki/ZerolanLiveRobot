from pydantic import BaseModel, Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from pipeline.asr.config import ASRPipelineConfig
from pipeline.imgcap.config import ImgCapPipelineConfig
from pipeline.llm.config import LLMPipelineConfig
from pipeline.ocr.config import OCRPipelineConfig
from pipeline.synch.abs_pipeline import AbstractPipelineConfig
from pipeline.synch.database import MilvusDatabaseConfig



#######
# TTS #
#######
class TTSModelIdEnum(BaseEnum):
    GPT_SoVITS = "AkagawaTsurunaki/GPT-SoVITS"  # Forked repo


class TTSPipelineConfig(AbstractPipelineConfig):
    model_id: TTSModelIdEnum = Field(default=TTSModelIdEnum.GPT_SoVITS,
                                     description=f"The ID of the model used for text-to-speech. \n"
                                                 f"{enum_to_markdown(TTSModelIdEnum)}")
    predict_url: str = Field(default="http://127.0.0.1:11000/tts/predict",
                             description="The URL for TTS prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/tts/stream-predict",
                                    description="The URL for streaming TTS prediction requests.")


##########
# VidCap #
##########
class VidCapModelIdEnum(BaseEnum):
    Hitea = 'iic/multi-modal_hitea_video-captioning_base_en'


class VidCapPipelineConfig(AbstractPipelineConfig):
    model_id: VidCapModelIdEnum = Field(default=VidCapModelIdEnum.Hitea,
                                        description=f"The ID of the model used for video captioning. \n"
                                                    f"{enum_to_markdown(VidCapModelIdEnum)}")
    predict_url: str = Field(default="http://127.0.0.1:11000/vid_cap/predict",
                             description="The URL for video captioning prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/vid-cap/stream-predict",
                                    description="The URL for streaming video captioning prediction requests.")


#######
# VLA #
#######
class ShowUIConfig(AbstractPipelineConfig):
    model_id: str = Field(default="showlab/ShowUI-2B", description="The ID of the model used for the UI.", frozen=True)
    predict_url: str = Field(default="http://127.0.0.1:11000/vla/showui/predict",
                             description="The URL for UI prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/vla/showui/stream-predict",
                                    description="The URL for streaming UI prediction requests.")


class VLAPipelineConfig(BaseModel):
    showui: ShowUIConfig = Field(default=ShowUIConfig(), description="Configuration for the ShowUI component.")
    enable: bool = Field(default=True, description="Whether the Visual Language Action pipeline is enabled.")


#########
# VecDB #
#########
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
