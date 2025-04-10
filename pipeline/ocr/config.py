from pydantic import Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from pipeline.synch.abs_pipeline import AbstractPipelineConfig


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
