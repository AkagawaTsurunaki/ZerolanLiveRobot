from typing import Generator, Any

import pyaudio
from loguru import logger

from common.config.model_config import SpeechParaformerModelConfig as spmc


class Microphone:

    def __init__(self):
        """
        注意：
            音频采样后会返回 bytes 类型，但是用 numpy 转换时，numpy 向量的 dtype 类型必须与使用麦克风的数据格式 format 一致，否则可能会发生异常。
        """
        self._stream = None
        self._chunk_size = 4096  # 每次读取的音频数据大小
        self._format = pyaudio.paFloat32  # 录制音频的格式，为了防止可能出现的错误，暂时硬编码为 Float32 格式
        self._channels = 1  # 声道数
        self._sample_rate = 16000  # 采样率（每秒采样点数）
        self._p = pyaudio.PyAudio()
        self._chunk_stride: int = spmc.chunk_stride
        self._is_recording: bool = False

    def open(self):
        logger.info("麦克风已开启")
        if self._is_recording:
            logger.warning("麦克风正在记录")
            return
        self._is_recording = True
        self._stream = self._p.open(format=self._format,
                                    channels=self._channels,
                                    rate=self._sample_rate,
                                    input=True,
                                    frames_per_buffer=self._chunk_size)

    def close(self):
        # 关闭音频输入流
        self._stream.stop_stream()
        self._stream.close()

        # 关闭 PyAudio
        self._p.terminate()
        self._is_recording = False
        logger.info("麦克风已关闭")

    def stream(self) -> Generator[bytes | None, Any, None]:
        try:
            while True:
                # 从音频输入流中读取音频数据
                data = self._stream.read(self._chunk_stride)
                yield data
        except Exception as e:
            logger.exception(e)
            yield None

    @property
    def is_recording(self):
        return self._is_recording