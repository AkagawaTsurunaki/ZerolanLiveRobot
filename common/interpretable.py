from abc import abstractmethod, ABCMeta


class Interpretable(metaclass=ABCMeta):
    @abstractmethod
    def interpret(self) -> str:
        pass

    @abstractmethod
    def is_meaningful(self) -> bool:
        pass
