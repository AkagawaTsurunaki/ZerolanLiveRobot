from pydantic import Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from common.utils.i18n_util import i18n_config
from pipeline.base.base_sync import AbstractPipelineConfig

_ = i18n_config()


#######
# OCR #
#######

class OCRModelIdEnum(BaseEnum):
    PaddleOCR = 'paddlepaddle/PaddleOCR'


class OCRPipelineConfig(AbstractPipelineConfig):
    model_id: OCRModelIdEnum = Field(default=OCRModelIdEnum.PaddleOCR,
                                     description=_(f"The ID of the model used for OCR. \n"
                                                   f"{enum_to_markdown(OCRModelIdEnum)}"))
    predict_url: str = Field(default="http://127.0.0.1:11000/ocr/predict",
                             description=_("The URL for OCR prediction requests."))
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/ocr/stream-predict",
                                    description=_("The URL for streaming OCR prediction requests."))
