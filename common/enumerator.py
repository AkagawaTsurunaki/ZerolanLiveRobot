from enum import Enum


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


class SystemSoundEnum(str, Enum):
    warn: str = "warn.wav"
    error: str = "error.wav"
    start: str = "start.wav"
    exit: str = "exit.wav"
    enable_func: str = "microphone-recoding.wav"
    disable_func: str = "microphone-stopped.wav"
    filtered: str = "filtered.wav"


class Action(str, Enum):
    PLAY_SPEECH = "play_speech"
    LOAD_LIVE2D_MODEL = "load_live2d_model"

    CLIENT_HELLO = "client_hello"
    SERVER_HELLO = "server_hello"

    LOAD_3D_MODEL = "load_model"
    UPDATE_GAMEOBJECTS_INFO = "update_gameobjects_info"
    QUERY_GAMEOBJECTS_INFO = "query_gameobjects_info"
    MODIFY_GAMEOBJECT_SCALE = "modify_gameobject_scale"
    CREATE_GAMEOBJECT = "create_gameobject"

    SHOW_USER_TEXT_INPUT = "show_user_text_input"
    ADD_HISTORY = "add_history"
