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
from event.registry import EventKeyRegistry
from services.game.minecraft.data import KonekoProtocol


class BaseEvent:
    type: str


@dataclass
class ASREvent(BaseEvent):
    prediction: ASRPrediction
    type: str = EventKeyRegistry.Pipeline.ASR


@dataclass
class QQMessageEvent(BaseEvent):
    message: str
    group_id: int | None
    type: str = EventKeyRegistry.QQBot.QQ_MESSAGE


@dataclass
class LLMEvent(BaseEvent):
    prediction: LLMPrediction
    type: str = EventKeyRegistry.Pipeline.LLM


@dataclass
class OCREvent(BaseEvent):
    prediction: OCRPrediction
    type: str = EventKeyRegistry.Pipeline.OCR


@dataclass
class TTSEvent(BaseEvent):
    prediction: TTSPrediction
    transcript: str
    type: str = EventKeyRegistry.Pipeline.TTS


@dataclass
class ImgCapEvent(BaseEvent):
    prediction: ImgCapPrediction
    type: str = EventKeyRegistry.Pipeline.IMG_CAP


@dataclass
class SpeechEvent(BaseEvent):
    speech: bytes
    channels: int
    sample_rate: int
    type: str = EventKeyRegistry.Device.SERVICE_VAD_SPEECH_CHUNK


@dataclass
class WebSocketJsonReceivedEvent(BaseEvent):
    data: any
    type: str = EventKeyRegistry._Inner.WEBSOCKET_RECV_JSON


@dataclass
class LiveStreamConnectedEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    type: str = EventKeyRegistry.LiveStream.CONNECTED


@dataclass
class LiveStreamDisconnectedEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    reason: str
    type: str = EventKeyRegistry.LiveStream.DISCONNECTED


@dataclass
class DanmakuEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    danmaku: Danmaku
    type: str = EventKeyRegistry.LiveStream.DANMAKU


@dataclass
class SuperChatEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    superchat: SuperChat
    type: str = EventKeyRegistry.LiveStream.SUPER_CHAT


@dataclass
class KonekoClientPushInstructionsEvent(BaseEvent):
    tools: List[Tool]
    type: str = EventKeyRegistry.Koneko.Client.PUSH_INSTRUCTIONS


@dataclass
class KonekoClientHelloEvent(BaseEvent):
    type = EventKeyRegistry.Koneko.Client.HELLO


@dataclass
class KonekoServerCallInstruction(BaseEvent):
    protocol_obj: KonekoProtocol
    type = EventKeyRegistry.Koneko.Server.CALL_INSTRUCTION


@dataclass
class ScreenCapturedEvent(BaseEvent):
    img: Image
    img_path: str
    type: str = EventKeyRegistry.Device.SCREEN_CAPTURED


@dataclass
class LanguageChangeEvent(BaseEvent):
    target_lang: str
    type: str = EventKeyRegistry.System.LANG_CHANGE


@dataclass
class SwitchVADEvent(BaseEvent):
    switch: bool
    type: str = EventKeyRegistry.Device.SWITCH_VAD


@dataclass
class PlaygroundConnectedEvent(BaseEvent):
    type: str = EventKeyRegistry.Playground.PLAYGROUND_CONNECTED
