import os

import pygame

from common.utils.audio_util import check_audio_format
from common.utils.file_util import create_temp_file, spath


class Speaker:

    def __init__(self):
        pygame.mixer.init()

    @staticmethod
    def playsound(path_or_data: str | bytes, block=True):
        if isinstance(path_or_data, bytes):
            path_or_data = Speaker._save_tmp_audio(path_or_data)
        if block:
            Speaker._sync_playsound(path_or_data)
        else:
            Speaker._async_playsound(path_or_data)

    @staticmethod
    def _sync_playsound(path: str):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

    @staticmethod
    def _async_playsound(path: str):
        sound = pygame.mixer.Sound(path)
        pygame.mixer.Sound.play(sound)

    @staticmethod
    def _save_tmp_audio(wave_data: bytes):
        format = check_audio_format(wave_data)
        wav_path = create_temp_file(prefix="tts", suffix=f".{format}", tmpdir="audio")
        with open(wav_path, "wb") as f:
            f.write(wave_data)
        return wav_path

    @staticmethod
    def play_system_sound(key: str, block: bool = False):
        Speaker.playsound(spath(os.path.join("resources/static/sound/system", key)), block)
