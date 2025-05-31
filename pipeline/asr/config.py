from pydantic import Field

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from common.utils.i18n_util import i18n_config
from pipeline.base.base_sync import AbstractPipelineConfig

_ = i18n_config()


#######
# ASR #
#######

class AudioFormatEnum(BaseEnum):
    Float32: str = "float32"


class ASRModelIdEnum(BaseEnum):
    Paraformer = "iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1"
    KotobaWhisper = 'kotoba-tech/kotoba-whisper-v2.0'


class ASRPipelineConfig(AbstractPipelineConfig):
    sample_rate: int = Field(16000, description=_("The sample rate for audio input."))
    channels: int = Field(1, description=_("The number of audio channels."))
    format: AudioFormatEnum = Field(AudioFormatEnum.Float32,
                                    description=_(
                                        "The format of the audio data: %s" % enum_to_markdown(AudioFormatEnum)))
    model_id: ASRModelIdEnum = Field(default=ASRModelIdEnum.Paraformer,
                                     description=_(
                                         f"The ID of the model used for ASR: %s" % enum_to_markdown(ASRModelIdEnum)))
    predict_url: str = Field(default="http://127.0.0.1:11000/asr/predict",
                             description=_("The URL for ASR prediction requests."))
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/asr/stream-predict",
                                    description=_("The URL for streaming ASR prediction requests."))
