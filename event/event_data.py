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
from services.game.minecraft.data import KonekoProtocol


class BaseEvent:
    type: str


@dataclass
class ASREvent(BaseEvent):
    prediction: ASRPrediction
    type: str = "pipeline/asr"


@dataclass
class LLMEvent(BaseEvent):
    prediction: LLMPrediction
    type: str = "pipeline/llm"


@dataclass
class OCREvent(BaseEvent):
    prediction: OCRPrediction
    type: str = "pipeline/ocr"


@dataclass
class TTSEvent(BaseEvent):
    prediction: TTSPrediction
    transcript: str
    type: str = "pipeline/tts"


@dataclass
class ImgCapEvent(BaseEvent):
    prediction: ImgCapPrediction
    type: str = "pipeline/img_cap"


@dataclass
class SpeechEvent(BaseEvent):
    speech: bytes
    channels: int
    sample_rate: int
    type: str = "service/vad/emit-speech-chunk"


@dataclass
class WebSocketJsonReceivedEvent(BaseEvent):
    data: any
    type: str = "websocket/json-received"


@dataclass
class LiveStreamConnectedEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    type: str = "service/live-stream/connected"


@dataclass
class LiveStreamDisconnectedEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    reason: str
    type: str = "service/live-stream/disconnected"


@dataclass
class DanmakuEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    danmaku: Danmaku
    type: str = "service/live-stream/danmaku"


@dataclass
class SuperChatEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    superchat: SuperChat
    type: str = "service/live-stream/super-chat"


@dataclass
class KonekoClientPushInstructionsEvent(BaseEvent):
    tools: List[Tool]
    type: str = "koneko/client/push-instructions"


@dataclass
class KonekoClientHelloEvent(BaseEvent):
    type: str = "koneko/client/hello"


@dataclass
class KonekoServerCallInstruction(BaseEvent):
    protocol_obj: KonekoProtocol
    type: str = "koneko/server/hello"


@dataclass
class ScreenCapturedEvent(BaseEvent):
    img: Image
    img_path: str
    type: str = "device/screen-captured"
