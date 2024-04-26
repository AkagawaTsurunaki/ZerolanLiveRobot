import os
import sys
import threading
from dataclasses import dataclass
from os import PathLike
from typing import List

from loguru import logger
from playsound import playsound

import utils.util
from common.abs_service import AbstractService, ServiceStatus
from utils.datacls import AudioPair
from obs.api import ObsService

# Config logger
logger.remove()
handler_id = logger.add(sys.stderr, level="INFO")


@dataclass
class AudioPlayerStatus(ServiceStatus):
    PLAYING = 'PLAYING'
    PAUSED = 'PAUSED'
    STOP = 'STOP'


class AudioPlayerService(AbstractService):

    def __init__(self, obs_service: ObsService):
        super().__init__()
        # List to store all audio pairs
        self.g_audio_list: List[AudioPair] = []

        # Add audio thread event, only after new AudioPair is added,
        # the audio play thread will run, reducing CPU usage
        self.add_audio_event: threading.Event = threading.Event()

        # Audio play event, used to control whether to play.
        self.audio_play_event: threading.Event = threading.Event()

        # Control whether break from dead loop
        self._running = False

        self._obs_service = obs_service

    def start(self):
        self._running = True
        self.audio_play_event.set()
        while self._running:
            self.add_audio_event.wait()
            self.audio_play_event.wait()
            audio_pair = self.select_latest_unplayed()
            if audio_pair:
                self._play(audio_pair)
            self.add_audio_event.clear()
        self.add_audio_event.clear()

    def stop(self):
        # Set all flags to false
        self._running = False
        self.add_audio_event.clear()
        self.audio_play_event.clear()
        # Save all audio files to the disk
        utils.util.save_service('audio_player', self.g_audio_list)
        # Reset audio list
        self.g_audio_list = []
        logger.warning('Audio player service has been stopped.')

    def _play(self, audio_pair: AudioPair):
        # To avoid error code 259, be sure to use the absolute path
        # And please do your own search for a solution to the coding problem.
        # Note: You need to modify the playsound source code because Windows does not use UTF-16.
        wav_file_path = os.path.abspath(audio_pair.wav_file_path)
        logger.debug(f'Playing audio file: "{wav_file_path}".')
        # TODO: Write obs subtitle here, will be refactored.
        self._obs_service.write_llm_output(text=audio_pair.transcript)
        playsound(wav_file_path)
        audio_pair.played = True
        logger.debug(f'Finished playing audio file: "{wav_file_path}".')

    def select_latest_unplayed(self):
        if len(self.g_audio_list) > 0:
            latest_unplayed_list = [item for item in self.g_audio_list if not item.played]
            if len(latest_unplayed_list) > 0:
                latest_unplayed = latest_unplayed_list[-1]
                latest_unplayed.played = True
                return latest_unplayed
        return None

    def add_audio(self, wav_file_path: str | PathLike, transcript: str):
        audiopair = AudioPair(transcript=transcript, wav_file_path=wav_file_path, played=False)
        self.g_audio_list.append(audiopair)
        self.add_audio_event.set()

    def pause(self):
        if self.audio_play_event.is_set():
            self.audio_play_event.clear()
            logger.info('Audio player service paused.')
        else:
            logger.warning('Invalid operation: Audio player service has been paused.')

    def resume(self):
        if not self.audio_play_event.is_set():
            self.audio_play_event.clear()
            logger.info('Audio player service resumed.')
        else:
            logger.warning('Invalid operation: Audio player service has been resumed.')

    def status(self) -> AudioPlayerStatus:
        if self._running:
            if self.audio_play_event.is_set():
                return AudioPlayerStatus.PLAYING
            else:
                return AudioPlayerStatus.PAUSED
        else:
            return AudioPlayerStatus.STOP
