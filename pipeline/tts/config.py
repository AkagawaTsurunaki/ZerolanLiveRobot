from pydantic import Field, BaseModel

from common.enumerator import BaseEnum
from common.utils.enum_util import enum_to_markdown
from pipeline.base.base_sync import AbstractPipelineConfig


#######
# TTS #
#######

class TTSModelIdEnum(BaseEnum):
    GPT_SoVITS = "AkagawaTsurunaki/GPT-SoVITS"  # Forked repo
    BaiduTTS = "BaiduTTS"


# Config for BaiduTTS and should
class BaiduTTSConfig(BaseModel):
    api_key: str = Field(default="", description="The API key for Baidu TTS service.")
    secret_key: str = Field(default="", description="The secret key for Baidu TTS service.")


# Config for ZerolanCore
class TTSPipelineConfig(AbstractPipelineConfig):
    model_id: TTSModelIdEnum = Field(default=TTSModelIdEnum.GPT_SoVITS,
                                     description=f"The ID of the model used for text-to-speech. \n"
                                                 f"{enum_to_markdown(TTSModelIdEnum)}")
    predict_url: str = Field(default="http://127.0.0.1:11000/tts/predict",
                             description="The URL for TTS prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/tts/stream-predict",
                                    description="The URL for streaming TTS prediction requests.")
    baidu_tts_config: BaiduTTSConfig = Field(default=BaiduTTSConfig(),
                                             description=f"Baidu TTS config. \n"
                                                         f"Only edit it when you set `model_id` to `{TTSModelIdEnum.BaiduTTS.value}`.\n"
                                                         f"For more details please see the [documents](https://cloud.baidu.com/doc/SPEECH/s/mlbxh7xie).")
