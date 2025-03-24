from abc import ABC, abstractmethod
from loguru import logger

from services.device.speaker import withsound
from common.enumerator import SystemSoundEnum


class AbstractFilter(ABC):

    @withsound(SystemSoundEnum.filtered)
    @abstractmethod
    def filter(self, content: str):
        pass


class FirstMatchedFilter:
    def __init__(self, words: list[str] = None) -> None:
        self.max_len = None
        self.min_len = None
        self.words = None

        if words is not None:
            self.set_words(words)

    def set_words(self, words: list[str]):
        self.words = words
        self.words.sort(key=lambda word: len(word))
        if len(self.words) > 0:
            self.min_len = len(self.words[0])
            self.max_len = len(self.words[-1])
        else:
            self.min_len = 0
            self.max_len = 0

    def filter(self, content: str | None) -> bool:
        if content is None:
            return False
        if len(content) < self.min_len:
            return False
        for word in self.words:
            if word in content:
                logger.warning(f"Filter detected bad word: {word}")
                return True
        return False
