from pydantic import Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from pipeline.base.base_sync import AbstractPipelineConfig

#################
# DEFENSE MODEL #
#################

class DefenseModelIdEnum(BaseEnum):
    Deberta_v3_base_prompt_injection_v2: str = "protectai/deberta-v3-base-prompt-injection-v2"


class DefenseModelPipelineConfig(AbstractPipelineConfig):
    enable: bool = Field(default=False, description="Whether the Defense Model is enabled. '❌' This part is still under development, just set 'False'.")
    api_key: str | None = Field(default=None, description="The API key for accessing the LLM service. \n" \
                                                          "No Supported model for now.")
    openai_format: bool = Field(default=False, description="Whether the output format is compatible with OpenAI. \n"
                                                           f"Note: When you use OpenAI models, please set it `true`.")
    model_id: DefenseModelIdEnum = Field(default=DefenseModelIdEnum.Deberta_v3_base_prompt_injection_v2,
                                     description=f"The ID of the model used for LLM. \n{enum_to_markdown(DefenseModelIdEnum)}")
    predict_url: str = Field(default="http://127.0.0.1:11012/defense/predict",
                             description="The URL for defense model prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11012/defense/stream-predict",
                                    description="The URL for streaming defense model prediction requests.")