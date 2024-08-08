from typing import List

from common.buffer.asb_buf import BufferObject, AbstractBuffer
from services.llm.pipeline import LLMPrediction


class LLMPredictionBufferObject(BufferObject):
    def __init__(self, p: LLMPrediction, priority: int = 0):
        super().__init__(priority=priority)
        self.llm_prediction: LLMPrediction = p


class LLMPredictionBuffer(AbstractBuffer):
    def __init__(self):
        super().__init__()
        self._buffer: List[LLMPredictionBufferObject] = []
