from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from config import GlobalConfig


@dataclass
class ServiceStatus(Enum):
    ...


class AbstractService(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def resume(self):
        pass

    @abstractmethod
    def status(self) -> ServiceStatus:
        pass
