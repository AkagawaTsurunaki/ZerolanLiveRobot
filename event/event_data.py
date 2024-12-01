from dataclasses import dataclass
from typing import List

from PIL.Image import Image
from zerolan.data.pipeline.asr import ASRPrediction
from zerolan.data.pipeline.img_cap import ImgCapPrediction
from zerolan.data.pipeline.llm import LLMPrediction
from zerolan.data.pipeline.ocr import OCRPrediction
from zerolan.data.pipeline.tts import TTSPrediction

from agent.tool_agent import Tool
from common.enumerator import EventEnum
from services.game.minecraft.data import KonekoProtocol


class BaseEvent:
    type: EventEnum


@dataclass
class ASREvent(BaseEvent):
    prediction: ASRPrediction
    type: EventEnum = EventEnum.PIPELINE_ASR


@dataclass
class LLMEvent(BaseEvent):
    prediction: LLMPrediction
    type: EventEnum = EventEnum.PIPELINE_LLM


@dataclass
class OCREvent(BaseEvent):
    prediction: OCRPrediction
    type: EventEnum = EventEnum.PIPELINE_OCR


@dataclass
class TTSEvent(BaseEvent):
    prediction: TTSPrediction
    type: EventEnum = EventEnum.PIPELINE_TTS


@dataclass
class ImgCapEvent(BaseEvent):
    prediction: ImgCapPrediction
    type: EventEnum = EventEnum.PIPELINE_IMG_CAP


@dataclass
class SpeechEvent(BaseEvent):
    speech: bytes
    channels: int
    sample_rate: int
    type: EventEnum = EventEnum.SERVICE_VAD_SPEECH_CHUNK


@dataclass
class KonekoClientPushInstructionsEvent(BaseEvent):
    tools: List[Tool]
    type: EventEnum = EventEnum.KONEKO_CLIENT_PUSH_INSTRUCTIONS


@dataclass
class KonekoClientHelloEvent(BaseEvent):
    type = EventEnum.KONEKO_CLIENT_HELLO


@dataclass
class KonekoServerCallInstruction(BaseEvent):
    protocol_obj: KonekoProtocol
    type = EventEnum.KONEKO_SERVER_CALL_INSTRUCTION


@dataclass
class ScreenCapturedEvent(BaseEvent):
    img: Image
    img_path: str
    type: EventEnum = EventEnum.DEVICE_SCREEN_CAPTURED
