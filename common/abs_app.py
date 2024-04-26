from abc import ABC, abstractmethod


class AbstractApp(ABC):
    def __init__(self):
        self.host: str
        self.port: int
        self.debug: bool

    @abstractmethod
    def start(self):
        pass