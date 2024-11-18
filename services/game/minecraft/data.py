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
    version: str = "0.2"
    type: str = "Hello"
    action: str = ""
    data: any = None


class ProtocolTypeEnum:
    Hello = "Hello"
    Fetch = "Fetch"
    Push = "Push"


class ActionEnum:
    DoNothing = "Do Nothing"
    GetInstructions = "Get Instructions"
    Quit = "Quit"


class Events:
    chat = "chat"
    login = "login"
