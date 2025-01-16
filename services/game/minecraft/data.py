from dataclasses import dataclass

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
    event: str = None
    data: dict | list = None

