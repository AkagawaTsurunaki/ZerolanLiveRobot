from dataclasses import dataclass

from pydantic import BaseModel


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
