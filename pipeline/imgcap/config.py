from pydantic import Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from pipeline.base.base_sync import AbstractPipelineConfig


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
