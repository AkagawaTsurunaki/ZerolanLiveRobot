from dataclasses import dataclass


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
