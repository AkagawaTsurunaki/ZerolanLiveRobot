import os
import threading
from enum import Enum
from functools import wraps
from queue import Queue

import pygame

from common.abs_runnable import ThreadRunnable
from common.killable_thread import KillableThread
from common.utils.audio_util import save_tmp_audio
from common.utils.file_util import spath

pygame.mixer.init()
_system_sound = False


class SystemSoundEnum(str, Enum):
    warn: str = "warn.wav"
    error: str = "error.wav"
    start: str = "start.wav"
    exit: str = "exit.wav"
    enable_func: str = "microphone-recoding.wav"
    disable_func: str = "microphone-stopped.wav"
    filtered: str = "filtered.wav"


class Speaker(ThreadRunnable):

    def name(self):
        return 'Speaker'

    def __init__(self):
        super().__init__()
        self._stop_flag = False
        self._semaphore = threading.Event()
        self._speaker_thread = KillableThread(target=self._run)
        self.audio_clips: Queue[str] = Queue()

    def start(self):
        super().start()
        self._stop_flag = False
        self._semaphore.set()
        self._speaker_thread.start()

    def stop(self):
        super().stop()
        self._stop_flag = True
        self.audio_clips = None
        self._speaker_thread.kill()

    def _run(self):
        while not self._stop_flag:

            if self.audio_clips.empty():
                self._semaphore.clear()
            self._semaphore.wait()

            audio_clip = self.audio_clips.get()
            self.playsound(audio_clip, block=True)

    def enqueue_sound(self, path_or_data: str | bytes):
        self.activate_check()
        if isinstance(path_or_data, bytes):
            path_or_data = save_tmp_audio(path_or_data)
        self.audio_clips.put(path_or_data)
        self._semaphore.set()

    def stop_now(self):
        pygame.mixer.stop()
        self.audio_clips = Queue()

    @staticmethod
    def playsound(path_or_data: str | bytes, block: bool = True):
        if isinstance(path_or_data, bytes):
            path_or_data = save_tmp_audio(path_or_data)
        if block:
            Speaker._sync_playsound(path_or_data)
        else:
            Speaker._async_playsound(path_or_data)

    @staticmethod
    def _sync_playsound(path: str):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        Speaker.wait()

    @staticmethod
    def wait():
        while pygame.mixer.music.get_busy():
            continue

    @staticmethod
    def _async_playsound(path: str):
        sound = pygame.mixer.Sound(path)
        pygame.mixer.Sound.play(sound)

    @staticmethod
    def play_system_sound(key: SystemSoundEnum, block: bool = False):
        if not _system_sound:
            return
        try:
            Speaker.playsound(spath(os.path.join("resources/static/sound/system", key.value)), block=block)
        except Exception as _:
            pass


def withsound(sound: SystemSoundEnum, block: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            Speaker.play_system_sound(sound, block)
            ret = func(*args, **kwargs)
            return ret

        return wrapper

    return decorator
