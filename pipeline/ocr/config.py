from pydantic import BaseModel, Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from pipeline.base.base_sync import AbstractPipelineConfig


#######
# OCR #
#######

class OCRModelIdEnum(BaseEnum):
    PaddleOCR = 'paddlepaddle/PaddleOCR'
    OtherOpenAIFormat = 'Other-OpenAI-Format'


class OpenAIFormatConfig(BaseModel):
    api_key: str = Field(default="", description="The API key for OpenAI-compatible API service.")
    base_url: str = Field(default="https://api.openai.com/v1",
                         description="The base URL for OpenAI-compatible API service. "
                                   "Default: https://api.openai.com/v1")
    model: str = Field(default="gpt-4o", description="The model name to use (e.g., gpt-4o, gemini-2.0-flash-lite-preview-02-05).")
    max_tokens: int = Field(default=500, description="Maximum number of tokens to generate.")


class OCRPipelineConfig(AbstractPipelineConfig):
    model_id: OCRModelIdEnum = Field(default=OCRModelIdEnum.PaddleOCR,
                                     description=f"The ID of the model used for OCR. \n"
                                                 f"{enum_to_markdown(OCRModelIdEnum)}")
    predict_url: str = Field(default="http://127.0.0.1:11000/ocr/predict",
                             description="The URL for OCR prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/ocr/stream-predict",
                                    description="The URL for streaming OCR prediction requests.")
    openai_format_config: OpenAIFormatConfig | None = Field(default=None,
                                                           description="Configuration for OpenAI-compatible format. "
                                                                     "Required when `model_id` is 'Other-OpenAI-Format'.")