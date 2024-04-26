from abc import ABC, abstractmethod

from config import GlobalConfig


class AbstractService(ABC):

    @abstractmethod
    def is_alive(self) -> bool:
        pass

    @abstractmethod
    def start(self, g_cfg: GlobalConfig):
        pass
