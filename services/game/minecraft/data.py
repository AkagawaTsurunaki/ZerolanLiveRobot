from dataclasses import dataclass

from dataclasses_json import dataclass_json
from pydantic import BaseModel

from common.enumerator import EventEnum


@dataclass_json
@dataclass
class BotOption:
    host: str
    port: int
    username: str
    version: str
    masterName: str


class KonekoProtocol(BaseModel):
    protocol: str = "Koneko Protocol"
    version: str = "0.2"
    event: EventEnum = None
    data: dict | list = None

