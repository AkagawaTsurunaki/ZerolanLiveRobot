import threading
from enum import Enum
from pathlib import Path
from queue import Queue

import pygame

from common.abs_runnable import ThreadRunnable
from common.killable_thread import KillableThread

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
        self.audio_clips: Queue[Path] = Queue()

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

    def enqueue_sound(self, path_or_data: Path):
        self.activate_check()
        self.audio_clips.put(path_or_data)
        self._semaphore.set()

    def stop_now(self):
        pygame.mixer.stop()
        self.audio_clips = Queue()

    @staticmethod
    def playsound(path: Path, block: bool = True):
        if block:
            Speaker._sync_playsound(path)
        else:
            Speaker._async_playsound(path)

    @staticmethod
    def _sync_playsound(path: Path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        Speaker.wait()

    @staticmethod
    def wait():
        while pygame.mixer.music.get_busy():
            continue

    @staticmethod
    def _async_playsound(path: Path):
        sound = pygame.mixer.Sound(path)
        pygame.mixer.Sound.play(sound)
