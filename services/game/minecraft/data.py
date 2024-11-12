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
    version: str = "0.1"
    bot_option: BotOption = None


class Events:
    chat = "chat"
    login = "login"
