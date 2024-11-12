from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class BotOption:
    host: str
    port: int
    username: str
    version: str
    masterName: str


@dataclass_json
@dataclass
class KonekoProtocol:
    protocol: str = "Koneko Protocol"
    version: str = "0.1"
    type: str = "hello"
    data: any = None


class Events:
    chat = "chat"
    login = "login"
