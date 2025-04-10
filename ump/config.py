from pydantic import BaseModel, Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from ump.abs_pipeline import AbstractPipelineConfig
from ump.pipeline.asr import ASRPipelineConfig
from ump.pipeline.database import MilvusDatabaseConfig
from ump.pipeline.img_cap import ImgCapPipelineConfig
from ump.pipeline.ocr import OCRPipelineConfig
from ump.pipeline.tts import TTSPipelineConfig
from ump.pipeline.vid_cap import VidCapPipelineConfig
from ump.pipeline.vla import ShowUIConfig


class LLMModelIdEnum(BaseEnum):
    DeepSeekAPI = "deepseek-chat"
    KimiAPI = "moonshot-v1-8k"

    ChatGLM3_6B = "THUDM/chatglm3-6b"
    GLM4 = "THUDM/GLM-4"
    Qwen_7B_Chat = "Qwen/Qwen-7B-Chat"
    Shisa_7b_V1 = "augmxnt/shisa-7b-v1"
    Yi_6B_Chat = "01-ai/Yi-6B-Chat"
    DeepSeek_R1_Distill = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"


# Paraformer: str = "iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1"


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
