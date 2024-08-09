import copy
from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

from common.buffer.asb_buf import AbstractBuffer, BufferObject


@dataclass_json
@dataclass
class MinecraftGameEvent(BufferObject):
    event: str
    message: str
    body: any


class MinecraftGameEventBuffer(AbstractBuffer):
    def __init__(self):
        super().__init__()
        self._buffer: List[MinecraftGameEvent] = []

    def select_last_one_and_clear(self):
        if self._buffer and len(self._buffer) > 0:
            ret = copy.deepcopy(self.get(-1))
            self.clear()
            return ret

        return None

    def select_last_one(self):
        if self._buffer:
            unread_event_list = [mgebo for mgebo in self._buffer if not mgebo.is_processed]
            if unread_event_list and len(unread_event_list) > 0:
                ret = self.get(-1)
                return ret
        return None
