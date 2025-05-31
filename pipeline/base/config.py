from pydantic import BaseModel, Field

from common.utils.i18n_util import i18n_config
from pipeline.asr.config import ASRPipelineConfig
from pipeline.db.milvus.config import VectorDBConfig
from pipeline.imgcap.config import ImgCapPipelineConfig
from pipeline.llm.config import LLMPipelineConfig
from pipeline.ocr.config import OCRPipelineConfig
from pipeline.tts.config import TTSPipelineConfig
from pipeline.vidcap.config import VidCapPipelineConfig
from pipeline.vla.config import VLAPipelineConfig

_ = i18n_config()


class PipelineConfig(BaseModel):
    asr: ASRPipelineConfig = Field(default=ASRPipelineConfig(),
                                   description=_("Configuration for the Automatic Speech Recognition pipeline."))
    llm: LLMPipelineConfig = Field(default=LLMPipelineConfig(),
                                   description=_("Configuration for the Large Language Model pipeline."))
    img_cap: ImgCapPipelineConfig = Field(default=ImgCapPipelineConfig(),
                                          description=_("Configuration for the Image Captioning pipeline."))
    ocr: OCRPipelineConfig = Field(default=OCRPipelineConfig(),
                                   description=_("Configuration for the Optical Character Recognition pipeline."))
    vid_cap: VidCapPipelineConfig = Field(default=VidCapPipelineConfig(),
                                          description=_("Configuration for the Video Captioning pipeline."))
    tts: TTSPipelineConfig = Field(default=TTSPipelineConfig(),
                                   description=_("Configuration for the Text-to-Speech pipeline."))
    vla: VLAPipelineConfig = Field(default=VLAPipelineConfig(),
                                   description=_("Configuration for the Visual Language Action pipeline."))
    vec_db: VectorDBConfig = Field(default=VectorDBConfig(), description=_("Configuration for the Vector Database."))
