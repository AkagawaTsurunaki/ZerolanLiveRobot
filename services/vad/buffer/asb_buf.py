import time
from abc import ABC
from typing import List, Callable
from loguru import logger


class BufferObject:
    def __init__(self, priority: int = 0) -> None:
        self.is_processed: bool = False
        self.is_filtered: bool = False
        self.time_stamp: float = time.time()
        self.priority: int = priority


class AbstractBuffer(ABC):
    def __init__(self):
        self._buffer: List[BufferObject] = []

    def append(self, obj: BufferObject):
        self._buffer.append(obj)

    def clear(self):
        self._buffer.clear()

    def get(self, i: int) -> BufferObject:
        try:
            bo = self._buffer[i]
            bo.is_processed = True
        except IndexError:
            logger.warning("AbstractBuffer 下标越界")
            bo = None
        return bo

    def select(self, func: Callable[[BufferObject], bool]) -> List[BufferObject]:
        result = []
        for obj in self._buffer:
            if func(obj):
                result.append(obj)
        return result

    def select_all_unprocessed(self) -> List[BufferObject]:
        result = []
        for obj in self._buffer:
            if not obj.is_processed:
                result.append(obj)
        return result

    def __len__(self):
        return len(self._buffer)