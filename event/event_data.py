from dataclasses import dataclass
from typing import List, Literal

from pydantic import BaseModel
from zerolan.data.data.danmaku import Danmaku, SuperChat
from zerolan.data.pipeline.asr import ASRPrediction
from zerolan.data.pipeline.img_cap import ImgCapPrediction
from zerolan.data.pipeline.llm import LLMPrediction
from zerolan.data.pipeline.ocr import OCRPrediction
from zerolan.data.pipeline.tts import TTSPrediction

from agent.tool_agent import Tool
from common.io.file_type import AudioFileType
from event.registry import EventKeyRegistry
from services.game.minecraft.data import KonekoProtocol
from services.live_stream.data import Gift


class BaseEvent(BaseModel):
    type: str


### System ###
class ConfigFileModifiedEvent(BaseEvent):
    type: str = EventKeyRegistry.System.CONFIG_FILE_MODIFIED


class LanguageChangeEvent(BaseEvent):
    target_lang: str
    type: str = EventKeyRegistry.System.LANG_CHANGE


class SystemUnhandledErrorEvent(BaseEvent):
    msg: str
    ex: any
    type: str = EventKeyRegistry.System.SYSTEM_UNHANDLED_ERROR


class SystemCrashedEvent(BaseEvent):
    type: str = EventKeyRegistry.System.SYSTEM_CRASHED


### Pipeline ###
class PipelineASREvent(BaseEvent):
    prediction: ASRPrediction
    type: str = EventKeyRegistry.Pipeline.ASR


class PipelineOutputLLMEvent(BaseEvent):
    prediction: LLMPrediction
    type: str = EventKeyRegistry.Pipeline.LLM


class PipelineOutputTTSEvent(BaseEvent):
    prediction: TTSPrediction
    transcript: str
    type: str = EventKeyRegistry.Pipeline.TTS


class PipelineImgCapEvent(BaseEvent):
    prediction: ImgCapPrediction
    type: str = EventKeyRegistry.Pipeline.IMG_CAP


class PipelineOCREvent(BaseEvent):
    prediction: OCRPrediction
    type: str = EventKeyRegistry.Pipeline.OCR


### Device ###
class DeviceScreenCapturedEvent(BaseEvent):
    img_path: str
    is_camera: bool
    type: str = EventKeyRegistry.Device.SCREEN_CAPTURED


class DeviceMicrophoneVADEvent(BaseEvent):
    speech: bytes
    audio_type: AudioFileType
    channels: int
    sample_rate: int
    type: str = EventKeyRegistry.Device.MICROPHONE_VAD


class DeviceMicrophoneSwitchEvent(BaseEvent):
    switch: bool
    type: str = EventKeyRegistry.Device.MICROPHONE_SWITCH


### Live streaming ###
class LiveStreamConnectedEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    type: str = EventKeyRegistry.LiveStream.CONNECTED


class LiveStreamDisconnectedEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    reason: str
    type: str = EventKeyRegistry.LiveStream.DISCONNECTED


class LiveStreamSuperChatEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    superchat: SuperChat
    type: str = EventKeyRegistry.LiveStream.SUPER_CHAT


class LiveStreamDanmakuEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    danmaku: Danmaku
    type: str = EventKeyRegistry.LiveStream.DANMAKU


class LiveStreamGiftEvent(BaseEvent):
    platform: Literal["bilibili", "twitch", "youtube"]
    gift: Gift
    type: str = EventKeyRegistry.LiveStream.GIFT


### Koneko Minecraft Bot ###
class KonekoClientPushInstructionsEvent(BaseEvent):
    tools: List[Tool]
    type: str = EventKeyRegistry.Koneko.Client.PUSH_INSTRUCTIONS


class KonekoClientHelloEvent(BaseEvent):
    type: str = EventKeyRegistry.Koneko.Client.HELLO


class KonekoServerCallInstruction(BaseEvent):
    protocol_obj: KonekoProtocol
    type: str = EventKeyRegistry.Koneko.Server.CALL_INSTRUCTION


### QQ ###
class QQMessageEvent(BaseEvent):
    message: str
    group_id: int | None
    type: str = EventKeyRegistry.QQBot.QQ_MESSAGE


### Zerolan Playground ###
class PlaygroundConnectedEvent(BaseEvent):
    type: str = EventKeyRegistry.Playground.CONNECTED


class PlaygroundDisconnectedEvent(BaseEvent):
    ws_id: str
    type: str = EventKeyRegistry.Playground.DISCONNECTED
