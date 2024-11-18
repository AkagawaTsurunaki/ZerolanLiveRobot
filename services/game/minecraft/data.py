from dataclasses import dataclass
from enum import Enum

from dataclasses_json import dataclass_json
from pydantic import BaseModel


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
    event: str = "Hello"
    data: any = None


class KonekoClientEventEnum(str, Enum):
    Hello = "koneko.client.hello"
    PushInstructions = "koneko.client.pushInstructions"


class Events:
    chat = "chat"
    login = "login"
