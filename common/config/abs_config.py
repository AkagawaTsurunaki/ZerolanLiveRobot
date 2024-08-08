from abc import ABC, abstractmethod


class AbstractConfigLoader(ABC):

    @staticmethod
    @abstractmethod
    def load_config():
        pass
