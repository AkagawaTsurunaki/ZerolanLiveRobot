from dataclasses import dataclass
from os import PathLike
from typing import Any, List

from common.abs_pipeline import AbstractModelQuery, AbstractModelResponse


@dataclass
class HTTPResponseBody:
    ok: bool
    msg: str
    data: Any = None


@dataclass
class Transcript:
    is_read: bool
    content: str


@dataclass
class Danmaku:
    is_read: bool  # 弹幕是否被阅读过
    uid: str  # 弹幕发送者UID
    username: str  # 弹幕发送者名称
    msg: str  # 弹幕发送内容
    ts: int  # 弹幕时间戳


@dataclass
class AudioPair:
    played: bool
    transcript: str
    wav_file_path: str | PathLike


@dataclass
class GPTSoVITSChangeRefer:
    refer_wav_path: str
    prompt_text: str
    prompt_language: str


@dataclass
class GPTSoVITSRequest:
    text: str
    text_language: str


@dataclass
class Tone:
    id: str
    refer_wav_path: str
    prompt_text: str
    prompt_language: str


@dataclass
class Chat:
    role: str
    content: str


@dataclass
class LLMResponse(AbstractModelResponse):
    response: str
    history: List[Chat]


@dataclass
class LLMQuery(AbstractModelQuery):
    text: str
    history: List[Chat]


@dataclass
class Role:
    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'


class ServiceNameConst:
    GPT_SOVITS = 'RVC-Boss/GPT-SoVITS'
    ASR = 'asr'
    BLIP = 'Salesforce/blip-image-captioning-large'
    CHATGLM3 = 'THUDM/chatglm3-6b'
    QWEN = 'Qwen/Qwen-7B-Chat'
    YI = '01-ai/Yi'
    SHISA = "augmxnt/shisa-7b-v1"
    PARAFORMER = "speech_paraformer"


@dataclass
class PlatformConst:
    BILIBILI = 'bilibili'


@dataclass
class WavFile:
    is_read: bool
    wav_file_path: str
