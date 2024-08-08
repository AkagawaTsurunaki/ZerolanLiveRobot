from abc import ABC, abstractmethod


class AbstractApplication(ABC):

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def _handle_predict(self):
        pass

    @abstractmethod
    def _handle_stream_predict(self):
        pass