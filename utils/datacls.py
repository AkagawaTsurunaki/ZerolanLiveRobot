from dataclasses import dataclass
from os import PathLike


@dataclass
class VAD:
    is_alive: bool
    pause: bool


@dataclass
class ZerolanServiceStatus:
    vad_service: VAD


@dataclass
class HTTPResponseBody:
    ok: bool
    msg: str
    data: ZerolanServiceStatus


def parse_http_response_body(json: dict) -> HTTPResponseBody:
    response = HTTPResponseBody(**json)
    vad = VAD(
        is_alive=response.data['vad_service']['is_alive'],
        pause=response.data['vad_service']['pause']
    )
    response.data = ZerolanServiceStatus(vad)
    return response


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
class LLMQuery:
    query: str
    history: list
    top_p: float
    temperature: float


@dataclass
class LLMResponse:
    response: str
    history: list[dict]


@dataclass
class AudioPair:
    played: bool
    transcript: str
    wav_file_path: str | PathLike
