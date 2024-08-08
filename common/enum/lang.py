from enum import Enum


class Language(Enum):
    ZH = "zh",
    EN = "en",
    JA = "ja"

    def name(self):
        if self == Language.ZH:
            return "zh"
        elif self == Language.EN:
            return "en"
        elif self == Language.JA:
            return "ja"
        else:
            raise ValueError("Unknown language")

    def to_zh_name(self):
        if self == Language.ZH:
            return "中文"
        elif self == Language.EN:
            return "英文"
        elif self == Language.JA:
            return "日语"
        else:
            raise ValueError("Unknown language")

    @staticmethod
    def value_of(s: str):
        s = s.lower()
        if s == "en":
            return Language.EN
        elif s == "zh":
            return Language.ZH
        elif s == "ja":
            return Language.JA
        else:
            raise ValueError("Unknown language")
