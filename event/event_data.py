from dataclasses import dataclass
from typing import List, Literal

from PIL.Image import Image
from zerolan.data.data.danmaku import Danmaku, SuperChat
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
class QQMessageEvent(BaseEvent):
    message: str
    group_id: int | None
    type: EventEnum = EventEnum.QQ_MESSAGE


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
    transcript: str
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
class WebSocketJsonReceivedEvent(BaseEvent):
    data: any
    type: EventEnum = EventEnum.WEBSOCKET_RECV_JSON


@dataclass
class LiveStreamConnectedEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    type: EventEnum = EventEnum.SERVICE_LIVE_STREAM_CONNECTED


@dataclass
class LiveStreamDisconnectedEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    reason: str
    type: EventEnum = EventEnum.SERVICE_LIVE_STREAM_DISCONNECTED


@dataclass
class DanmakuEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    danmaku: Danmaku
    type: EventEnum = EventEnum.SERVICE_LIVE_STREAM_DANMAKU


@dataclass
class SuperChatEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    superchat: SuperChat
    type: EventEnum = EventEnum.SERVICE_LIVE_STREAM_SUPER_CHAT


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


@dataclass
class LanguageChangeEvent(BaseEvent):
    target_lang: str
    type: EventEnum = EventEnum.LANG_CHANGE


@dataclass
class OpenMicrophoneEvent(BaseEvent):
    type: EventEnum = EventEnum.OPEN_MICROPHONE


@dataclass
class CloseMicrophoneEvent(BaseEvent):
    type: EventEnum = EventEnum.CLOSE_MICROPHONE
