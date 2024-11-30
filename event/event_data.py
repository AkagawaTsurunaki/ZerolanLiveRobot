from dataclasses import dataclass
from enum import Enum


class EventType(str, Enum):
    EXIT = "exit"
    START = "start"


class BaseEvent:
    type: EventType


@dataclass
class SleepEvent(BaseEvent):
    sleep_time: float
    type: EventType = EventType.EXIT
