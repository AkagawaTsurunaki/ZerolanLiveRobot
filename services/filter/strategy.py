from abc import ABC, abstractmethod
from loguru import logger

class AbstractFilter(ABC):

    @abstractmethod
    def filter(self, content: str):
        pass

class FirstMatchedFilter:
    def __init__(self) -> None:
        self.words = []
        self.words.sort(key=lambda word: len(word))
        if len(self.words) > 0:
            self.min_len = self.words[0]
            self.max_len = self.words[-1]
        else:
            self.min_len = 0
            self.max_len = 0

    def filter(self, content: str | None) -> bool:
        if content is None:
            return True
        if len(content) < self.min_len:
            return True
        for word in self.words:
            if word in content:
                logger.warning(f"触发敏感词: {word}")
                return False
        return True
    
_content_filter = FirstMatchedFilter()
    
def content_filter() -> AbstractFilter:
    # 默认使用首次匹配内容过滤器
    return _content_filter