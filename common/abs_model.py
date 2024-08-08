from abc import ABC, abstractmethod
from typing import Any


class AbstractModel(ABC):

    def __init__(self):
        self.model_id = None

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def predict(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def stream_predict(self, *args, **kwargs) -> Any:
        pass
