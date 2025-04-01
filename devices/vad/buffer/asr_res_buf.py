import numpy as np

from devices.vad.buffer.asb_buf import AbstractBuffer


class AudioBuffer(AbstractBuffer):
    """
    假设均为 16000 采样率, 单声道。
    """

    def __init__(self, win_sz: int | None = None):
        super().__init__()
        self.pointer: int = 0  # 注意：如果缓冲为空列表，那么 pointer 会为 -1
        self._speech_chunk_list: list[np.ndarray] = []
        self._win_size: int | None = win_sz

    def append(self, chunk: np.ndarray):
        self._speech_chunk_list.append(chunk)
        self.pointer = len(self._speech_chunk_list) - 1

    def read_all(self):
        len_list = len(self._speech_chunk_list)

        if self._win_size and len_list >= self._win_size:
            chunks = self._speech_chunk_list[len_list - self._win_size:]
            return np.concatenate(chunks, axis=0)

        return np.concatenate(self._speech_chunk_list, axis=0)

    def empty(self):
        return len(self._speech_chunk_list) == 0

    def flush(self):
        self._speech_chunk_list = []
        self.pointer = -1
