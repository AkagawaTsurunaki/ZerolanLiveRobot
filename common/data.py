from dataclasses import dataclass

from dataclasses_json import dataclass_json
from zerolan.data.data.tts import TTSQuery


@dataclass_json
@dataclass
class TTSPrompt:
    audio_path: str
    lang: str # Use enum.Language
    sentiment: str
    prompt_text: str


@dataclass_json
@dataclass
class GPT_SoVITS_TTS_Query(TTSQuery):
    cut_punc: str = "，。"
