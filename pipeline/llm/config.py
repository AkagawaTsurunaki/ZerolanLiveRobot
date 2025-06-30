from pydantic import Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from pipeline.base.base_sync import AbstractPipelineConfig


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
