from pydantic import BaseModel, Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from pipeline.synch.abs_pipeline import AbstractPipelineConfig
from pipeline.synch.database import MilvusDatabaseConfig


#######
# ASR #
#######
class AudioFormatEnum(BaseEnum):
    Float32: str = "float32"


class ASRModelIdEnum(BaseEnum):
    Paraformer = "iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1"
    KotobaWhisper = 'kotoba-tech/kotoba-whisper-v2.0'


class ASRPipelineConfig(AbstractPipelineConfig):
    sample_rate: int = Field(16000, description="The sample rate for audio input.")
    channels: int = Field(1, description="The number of audio channels.")
    format: AudioFormatEnum = Field(AudioFormatEnum.Float32,
                                    description=f"The format of the audio data. {enum_to_markdown(AudioFormatEnum)}")
    model_id: ASRModelIdEnum = Field(default=ASRModelIdEnum.Paraformer,
                                     description=f"The ID of the model used for ASR. \n{enum_to_markdown(ASRModelIdEnum)}")
    predict_url: str = Field(default="http://127.0.0.1:11000/asr/predict",
                             description="The URL for ASR prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/asr/stream-predict",
                                    description="The URL for streaming ASR prediction requests.")


#######
# LLM #
#######
class LLMModelIdEnum(BaseEnum):
    DeepSeekAPI: str = "deepseek-chat"
    KimiAPI: str = "moonshot-v1-8k"

    ChatGLM3_6B: str = "THUDM/chatglm3-6b"
    GLM4: str = "THUDM/GLM-4"
    Qwen_7B_Chat: str = "Qwen/Qwen-7B-Chat"
    Shisa_7b_V1: str = "augmxnt/shisa-7b-v1"
    Yi_6B_Chat: str = "01-ai/Yi-6B-Chat"
    DeepSeek_R1_Distill: str = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"


class LLMPipelineConfig(AbstractPipelineConfig):
    api_key: str | None = Field(default=None, description="The API key for accessing the LLM service.　\n"
                                                          "Kimi API supported: \n"
                                                          "Reference: https://platform.moonshot.cn/docs/guide/start-using-kimi-api \n"
                                                          "Deepseek API supported: \n"
                                                          "Reference: https://api-docs.deepseek.com/zh-cn/")
    openai_format: bool = Field(default=False, description="Whether the output format is compatible with OpenAI. \n"
                                                           f"Note: When you use `{LLMModelIdEnum.DeepSeekAPI}` or {LLMModelIdEnum.KimiAPI}, please set it `true`.")
    model_id: LLMModelIdEnum = Field(default=LLMModelIdEnum.GLM4,
                                     description=f"The ID of the model used for LLM. \n{enum_to_markdown(LLMModelIdEnum)}")
    predict_url: str = Field(default="http://127.0.0.1:11000/llm/predict",
                             description="The URL for LLM prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/llm/stream-predict",
                                    description="The URL for streaming LLM prediction requests.")


##########
# ImgCap #
##########
class ImgCapModelIdEnum(BaseEnum):
    Blip = 'Salesforce/blip-image-captioning-large'


class ImgCapPipelineConfig(AbstractPipelineConfig):
    model_id: ImgCapModelIdEnum = Field(default=ImgCapModelIdEnum.Blip,
                                        description=f"The ID of the model used for image captioning. "
                                                    f"\n{enum_to_markdown(ImgCapModelIdEnum)}")
    predict_url: str = Field(default="http://127.0.0.1:11000/img-cap/predict",
                             description="The URL for image captioning prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/img-cap/stream-predict",
                                    description="The URL for streaming image captioning prediction requests.")


#######
# OCR #
#######
class OCRModelIdEnum(BaseEnum):
    PaddleOCR = 'paddlepaddle/PaddleOCR'


class OCRPipelineConfig(AbstractPipelineConfig):
    model_id: OCRModelIdEnum = Field(default=OCRModelIdEnum.PaddleOCR,
                                     description=f"The ID of the model used for OCR. \n"
                                                 f"{enum_to_markdown(OCRModelIdEnum)}")
    predict_url: str = Field(default="http://127.0.0.1:11000/ocr/predict",
                             description="The URL for OCR prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/ocr/stream-predict",
                                    description="The URL for streaming OCR prediction requests.")


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
