from pydantic import Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from common.utils.i18n_util import i18n_config
from pipeline.base.base_sync import AbstractPipelineConfig

_ = i18n_config()


##########
# ImgCap #
##########

class ImgCapModelIdEnum(BaseEnum):
    Blip = 'Salesforce/blip-image-captioning-large'


class ImgCapPipelineConfig(AbstractPipelineConfig):
    model_id: ImgCapModelIdEnum = Field(default=ImgCapModelIdEnum.Blip,
                                        description=_(
                                            "The ID of the model used for image captioning: %s" % enum_to_markdown(
                                                ImgCapModelIdEnum)))
    predict_url: str = Field(default="http://127.0.0.1:11000/img-cap/predict",
                             description=_("The URL for image captioning prediction requests."))
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/img-cap/stream-predict",
                                    description=_("The URL for streaming image captioning prediction requests."))
