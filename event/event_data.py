from dataclasses import dataclass

from zerolan.data.pipeline.asr import ASRPrediction

from common.enumerator import EventEnum


class BaseEvent:
    type: EventEnum


@dataclass
class ASREvent(BaseEvent):
    prediction: ASRPrediction
    type: EventEnum = EventEnum.PIPELINE_ASR


@dataclass
class SpeechEvent(BaseEvent):
    speech: bytes
    channels: int
    sample_rate: int
    type: EventEnum = EventEnum.SERVICE_VAD_SPEECH_CHUNK
