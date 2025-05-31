from pydantic import Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from common.utils.i18n_util import i18n_config
from pipeline.base.base_sync import AbstractPipelineConfig

_ = i18n_config()


##########
# VidCap #
##########

class VidCapModelIdEnum(BaseEnum):
    Hitea = 'iic/multi-modal_hitea_video-captioning_base_en'


class VidCapPipelineConfig(AbstractPipelineConfig):
    model_id: VidCapModelIdEnum = Field(default=VidCapModelIdEnum.Hitea,
                                        description=_(f"The ID of the model used for video captioning. \n"
                                                      f"{enum_to_markdown(VidCapModelIdEnum)}"))
    predict_url: str = Field(default="http://127.0.0.1:11000/vid_cap/predict",
                             description=_("The URL for video captioning prediction requests."))
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/vid-cap/stream-predict",
                                    description=_("The URL for streaming video captioning prediction requests."))
