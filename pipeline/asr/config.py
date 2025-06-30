from pydantic import Field, BaseModel

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from pipeline.base.base_sync import AbstractPipelineConfig


#######
# ASR #
#######

class AudioFormatEnum(BaseEnum):
    Float32: str = "float32"


class ASRModelIdEnum(BaseEnum):
    Paraformer = "iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1"
    KotobaWhisper = 'kotoba-tech/kotoba-whisper-v2.0'
    BaiduASR = "BaiduASR"


class BaiduASRConfig(BaseModel):
    api_key: str = Field(default="", description="The API key for Baidu ASR service.")
    secret_key: str = Field(default="", description="The secret key for Baidu ASR service.")


class ASRPipelineConfig(AbstractPipelineConfig):
    sample_rate: int = Field(16000, description="The sample rate for audio input.")
    channels: int = Field(1, description="The number of audio channels.")
    format: AudioFormatEnum = Field(AudioFormatEnum.Float32,
                                    description=f"The format of the audio data. {enum_to_markdown(AudioFormatEnum)}")
    model_id: ASRModelIdEnum = Field(default=ASRModelIdEnum.Paraformer,
                                     description=f"The ID of the model used for ASR. \n{enum_to_markdown(ASRModelIdEnum)}")
    predict_url: str = Field(default="http://127.0.0.1:11000/asr/predict",
                             description="The URL for ASR prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/asr/stream-predict",
                                    description="The URL for streaming ASR prediction requests.")
    baidu_asr_config: BaiduASRConfig = Field(default=BaiduASRConfig(), description="Baidu ASR config."
                                                                                   f"Only edit it when you set `model_id` to `{ASRModelIdEnum.BaiduASR.value}`.\n"
                                                                                   f"For more details please see the [documents](https://cloud.baidu.com/doc/SPEECH/s/qlcirqhz0).")
