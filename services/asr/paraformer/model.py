"""
模型 ID：
    speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1
更多内容详见：
    https://modelscope.cn/models/iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1
"""

import numpy as np
from funasr import AutoModel
from loguru import logger

from common.config.model_config import ModelConfigLoader
from common.register.model_register import ASRModels
from common.utils import audio_util
from common.decorator import log_model_loading
from services.asr.pipeline import ASRModelPrediction, ASRModelQuery, ASRModelStreamQuery

config = ModelConfigLoader.speech_paraformer_model_config


class SpeechParaformerModel:

    def __init__(self):
        self._model: any = None
        # 流式推理配置
        # 注：chunk_size为流式延时配置，
        # [0,10,5]表示上屏实时出字粒度为10*60=600ms，未来信息为5*60=300ms。
        # 每次推理输入为600ms（采样点数为16000*0.6=960），输出为对应文字，
        # 最后一个语音片段输入需要设置is_final=True来强制输出最后一个字。
        self._sample_rate = 16000  # 使用其它采样率将会报错
        self.dtype = np.float32

        self._chunk_size = config.chunk_size
        self._encoder_chunk_look_back = config.encoder_chunk_look_back
        self._decoder_chunk_look_back = config.decoder_chunk_look_back
        self._model_path = config.model_path
        self._version = config.version
        self._chunk_stride = config.chunk_stride
        self._cache = {}
        self._is_final = False

    @log_model_loading(ASRModels.SPEECH_PARAFORMER_ASR)
    def load_model(self):
        """
        加载模型。
        """
        self._model = AutoModel(model=self._model_path, model_revision=self._version)
        assert self._model

    def predict(self, query: ASRModelQuery) -> ASRModelPrediction | None:

        """
        推理。
        Args:
            query: 包含采样率为 16000 且为单声道的音频数据

        Returns:

        """
        wave_nparray, sample_rate = audio_util.from_file_to_np_array(query.audio_path, self.dtype.__name__)
        assert sample_rate and sample_rate == self._sample_rate, "采样率必须为 16000，否则识别结果会出现严重偏差。"
        is_final = query.audio_path is None

        return self._wrapper(wave_nparray, is_final)

    def stream_predict(self, query: ASRModelStreamQuery) -> ASRModelPrediction | None:
        """
        流式推理。
        Args:
            speech: 采样率为 16000 且为单声道的音频数据

        Returns:

        """
        wave_nparray, sample_rate = audio_util.from_bytes_to_np_ndarray(query.audio_data, self.dtype.__name__)
        assert sample_rate and sample_rate == self._sample_rate, "采样率必须为 16000，否则识别结果会出现严重偏差。"
        return self._wrapper(wave_nparray, query.is_final)

    def _wrapper(self, wave_nparray: np.ndarray, is_final: bool) -> ASRModelPrediction | None:
        assert wave_nparray is not None and isinstance(wave_nparray, np.ndarray), "格式不正确"
        assert len(wave_nparray) > 0, "音频张量大小必须大于 0"
        assert len(wave_nparray.shape) == 1, "音频必须为单声道音频"
        assert wave_nparray.dtype == np.float32, "暂不支持的 dtype 类型，目前必须为 numpy.float32"
        try:
            res = self._model.generate(input=wave_nparray, cache=self._cache, is_final=is_final,
                                       chunk_size=self._chunk_size,
                                       encoder_chunk_look_back=self._encoder_chunk_look_back,
                                       decoder_chunk_look_back=self._decoder_chunk_look_back)
            transcript = res[0]["text"]

            return ASRModelPrediction(transcript)
        except IndexError as e:
            if "IndexError: list index out of range" in str(e):
                logger.warning("推理意外结束")
            return None
        except AssertionError as e:
            if "AssertionError: choose a window size" in str(e):
                logger.warning("音频张量大小错误")
            logger.exception(e)
            return None
        except Exception as e:
            logger.exception(e)
            return None
