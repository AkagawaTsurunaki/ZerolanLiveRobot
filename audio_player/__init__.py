from dataclasses import dataclass
from os import PathLike


@dataclass
class AudioPair:
    transcript: str
    wav_file_path: str | PathLike