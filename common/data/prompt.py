from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class TTSPrompt:
    audio_path: str
    lang: str # Use enum.Language
    sentiment: str
    prompt_text: str
