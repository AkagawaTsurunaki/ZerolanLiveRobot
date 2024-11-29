import numpy as np

from common.utils.math_util import clamp
from services.vad.buffer.asr_res_buf import AudioBuffer


class EasyEnergyVad:

    def __init__(self, threshold: int = 100, max_mute_count: int = 2, pad: int = 1):
        """

        Args:
            threshold: 能量判断阈值，取决于您所在的环境。
            max_mute_count: 连续 max_mute_count 个音频块低于能量判断阈值 threshold，将会被判断为无人声。
            pad: 规定在音频缓冲切片的前后填充多少个块。
                 例如，当第 k 个块被判断为有人声，第 n 个块被判断为连续 max_mute_count 次无人声时，
                 会在将 k - pad 作为切片起点，以 n - max_mute_count + pad 作为切片终点。
        """
        # 构造器参数赋值
        self._threshold: int = threshold
        self._max_mute_count = max_mute_count
        self._pad = pad

        # 内部维护的值，可按需重置
        self._buf: AudioBuffer = AudioBuffer()
        self._start_index = -1
        self._end_index = -1
        self._mute_count = 0

    def reset_stream(self):
        """
        重置人声检测流逻辑。
        """
        # 清除缓存，防止内存泄露
        self._buf.flush()

        # 重置索引和计数器
        self._start_index = -1
        self._end_index = -1
        self._mute_count = 0

    def is_speech(self, speech_chunk: np.ndarray) -> bool:
        """
        判断该音频块是否有人声。
        如果该音频块的每一个采样点的绝对值之和大于 self.threshold，那么判断为有人声。

        Args:
            speech_chunk: 一维音频向量，单通道。

        Returns:
            True - 当音频包含人声。

            False - 当音频未包含人声。
        """
        energy = np.sum(np.abs(speech_chunk))
        return energy > self._threshold

    def check_stream(self, speech_chunk: np.ndarray) -> np.ndarray | None:
        """
        流式音频块人声切片。
        这将会使用内部音频缓冲，每次调用此函数，AudioBuffer 将写入一个 speech_chunk。
        当有连续 max_mute_count 个音频块低于能量判断阈值 threshold，将会返回填充（Padding）切片并清除音频缓冲。
        Args:
            speech_chunk: 音频块。

        Returns:
            仅人声的音频切片。会自动拼接之前调用函数时，留在 AudioBuffer 中的音频块。
            如果返回 None，表示当前流中没有检测到人声片段。
        Warnings:
            如果流被切断，请注意务必调用 reset_stream()。
        """

        # logger.debug(self._mute_count)

        # 将音频块存储进缓存
        self._buf.append(speech_chunk)

        # 读取缓存
        speech = self._buf.read_all()
        assert not self._buf.empty(), f"Audio Buffer 异常"

        if self.is_speech(speech_chunk):
            if self._start_index < 0:
                self._start_index = clamp(0, self._buf.pointer, self._buf.pointer - self._pad)
            self._mute_count = 0
        else:
            self._mute_count += 1
            self._end_index = clamp(0, self._buf.pointer, self._buf.pointer - self._max_mute_count + self._pad)

        # logger.debug(f"当前音频切片索引为 [{self._start_index}: {self._end_index}]")

        if self._mute_count > self._max_mute_count:
            self.reset_stream()
            # logger.debug(f"因为达到连续最大静息数 {self._max_mute_count}，VAD 音频缓存已清空")

        if self._start_index >= 0 and (not self._buf.empty()):
            real_speech = speech[self._start_index * len(speech_chunk):]
            assert len(real_speech) > 0, "音频张量切片的长度应该大于 0"

            return real_speech

        return None
