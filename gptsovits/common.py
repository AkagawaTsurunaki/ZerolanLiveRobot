from dataclasses import dataclass


@dataclass
class Request:
    text: str
    text_language: str
