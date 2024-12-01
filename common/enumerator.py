from enum import Enum


class Language:
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


class EventEnum(str, Enum):
    """
    All event names should be registered here.
    """
    TEST = "test"

    SYSTEM_ERROR = "system.error"
    SYSTEM_CRASHED = "system.crashed"

    PIPELINE_ASR = "pipeline.asr"
    PIPELINE_LLM = "pipeline.llm"
    PIPELINE_TTS = "pipeline.tts"
    PIPELINE_IMG_CAP = "pipeline.img_cap"
    PIPELINE_OCR = "pipeline.ocr"

    DEVICE_SCREEN_CAPTURED = "device.screen_captured"

    SERVICE_LIVE_STREAM_CONNECTED = "service.live_stream.connected"
    SERVICE_LIVE_STREAM_DISCONNECTED = "service.live_stream.disconnected"
    SERVICE_LIVE_STREAM_DANMAKU = "service.live_stream.danmaku"
    SERVICE_LIVE_STREAM_GIFT = "service.live_stream.gift"
    SERVICE_LIVE_STREAM_SUPER_CHAT = "service.live_stream.super_chat"

    SERVICE_VAD_SPEECH_CHUNK = "service.vad.speech_chunk"

    KONEKO_CLIENT_HELLO = "koneko.client.hello"
    KONEKO_CLIENT_PUSH_INSTRUCTIONS = "koneko.client.push_instructions"
    KONEKO_SERVER_HELLO = "koneko.server.hello"
    KONEKO_SERVER_FETCH_INSTRUCTIONS = "koneko.server.fetch_instructions"
    KONEKO_SERVER_CALL_INSTRUCTION = "koneko.server.call_instruction"

    WEBSOCKET_RECV_JSON = "websocket.recv.json"
