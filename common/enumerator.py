from enum import Enum


class BaseEnum(str, Enum):
    pass


class Language(str, Enum):
    ZH = "zh"
    EN = "en"
    JA = "ja"

    def full_name(self):
        if self == self.ZH:
            return "Chinese"
        elif self == self.EN:
            return "English"
        elif self == self.JA:
            return "Japanese"
        else:
            raise ValueError("Unknown language")

    def name(self):
        if self == self.ZH:
            return "zh"
        elif self == self.EN:
            return "en"
        elif self == self.JA:
            return "ja"
        else:
            raise ValueError("Unknown language")

    def to_zh_name(self):
        if self == self.ZH:
            return "中文"
        elif self == self.EN:
            return "英文"
        elif self == self.JA:
            return "日语"
        else:
            raise ValueError("Unknown language")

    @staticmethod
    def value_of(s: str):
        s = s.lower()
        if s in ["en", "english", "英文", "英语"]:
            return Language.EN
        elif s in ["zh", "cn", "chinese", "中文"]:
            return Language.ZH
        elif s in ["ja", "japanese", "日语", "日本語", "にほんご"]:
            return Language.JA
        else:
            raise ValueError("Unknown language")
