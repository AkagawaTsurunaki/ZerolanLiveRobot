from pydantic import Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from common.utils.i18n_util import i18n_config
from pipeline.base.base_sync import AbstractPipelineConfig

_ = i18n_config()


#######
# TTS #
#######

class TTSModelIdEnum(BaseEnum):
    GPT_SoVITS = "AkagawaTsurunaki/GPT-SoVITS"  # Forked repo


class TTSPipelineConfig(AbstractPipelineConfig):
    model_id: TTSModelIdEnum = Field(default=TTSModelIdEnum.GPT_SoVITS,
                                     description=_(f"The ID of the model used for text-to-speech. \n"
                                                   f"{enum_to_markdown(TTSModelIdEnum)}"))
    predict_url: str = Field(default="http://127.0.0.1:11000/tts/predict",
                             description=_("The URL for TTS prediction requests."))
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/tts/stream-predict",
                                    description=_("The URL for streaming TTS prediction requests."))
