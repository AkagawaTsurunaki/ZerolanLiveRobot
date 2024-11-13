import pygame

from common.utils.audio_util import check_audio_format
from common.utils.file_util import create_temp_file


class Speaker:

    def playsound(self, path_or_data: str | bytes):
        if isinstance(path_or_data, bytes):
            self._playsound_bytes(path_or_data)
        else:
            self._playsound_file(path_or_data)

    def _playsound_file(self, path: str, block=True):
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        if block:
            while pygame.mixer.music.get_busy():
                continue

    def _playsound_bytes(self, wave_data: bytes, block=True):
        format = check_audio_format(wave_data)
        wav_path = create_temp_file(prefix="tts", suffix=f".{format}", tmpdir="audio")
        with open(wav_path, "wb") as f:
            f.write(wave_data)
        self._playsound_file(wav_path, block)
