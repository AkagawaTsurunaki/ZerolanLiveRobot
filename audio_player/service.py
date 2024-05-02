import os
import sys
import threading
from os import PathLike
from typing import List

from loguru import logger
from playsound import playsound

from common.datacls import AudioPair, AudioPlayerStatus
from config import GLOBAL_CONFIG as G_CFG

# Config logger
logger.remove()
handler_id = logger.add(sys.stderr, level="INFO")

_audio_list: List[AudioPair]
_add_audio_event: threading.Event
_audio_play_event: threading.Event
_running: bool


def init():
    global _audio_list, _add_audio_event, _audio_play_event, _running
    # List to store all audio pairs
    _audio_list = []

    # Add audio thread event, only after new AudioPair is added,
    # the audio play thread will run, reducing CPU usage
    _add_audio_event = threading.Event()

    # Audio play event, used to control whether to play.
    _audio_play_event = threading.Event()

    # Control whether break from dead loop
    _running = False


def start():
    global _running
    _running = True
    _audio_play_event.set()
    while _running:
        _add_audio_event.wait()
        _audio_play_event.wait()
        audio_pair = select_latest_unplayed()
        if audio_pair:
            _play(audio_pair)
        _add_audio_event.clear()
    _add_audio_event.clear()


def stop():
    global _running, _audio_list
    # Set all flags to false
    _running = False
    _add_audio_event.clear()
    _audio_play_event.clear()
    # Reset audio list
    _audio_list = []
    logger.warning('Audio player service has been stopped.')


def _play(audio_pair: AudioPair):
    # To avoid error code 259, be sure to use the absolute path
    # And please do your own search for a solution to the coding problem.
    # Note: You need to modify the playsound source code because Windows does not use UTF-16.
    wav_file_path = os.path.abspath(audio_pair.wav_file_path)
    logger.debug(f'Playing audio file: "{wav_file_path}".')
    # TODO: Write obs subtitle here, will be refactored.
    if G_CFG.obs.enable:
        import obs.api
        obs.api.write_llm_output(text=audio_pair.transcript)
    playsound(wav_file_path)
    audio_pair.played = True
    logger.debug(f'Finished playing audio file: "{wav_file_path}".')


def select_latest_unplayed():
    if len(_audio_list) > 0:
        latest_unplayed_list = [item for item in _audio_list if not item.played]
        if len(latest_unplayed_list) > 0:
            latest_unplayed = latest_unplayed_list[-1]
            latest_unplayed.played = True
            return latest_unplayed
    return None


def add_audio(wav_file_path: str | PathLike, transcript: str):
    audiopair = AudioPair(transcript=transcript, wav_file_path=wav_file_path, played=False)
    _audio_list.append(audiopair)
    _add_audio_event.set()


def pause():
    if _audio_play_event.is_set():
        _audio_play_event.clear()
        logger.info('Audio player service paused.')
    else:
        logger.warning('Invalid operation: Audio player service has been paused.')


def resume():
    if not _audio_play_event.is_set():
        _audio_play_event.clear()
        logger.info('Audio player service resumed.')
    else:
        logger.warning('Invalid operation: Audio player service has been resumed.')


def status() -> AudioPlayerStatus:
    if _running:
        if _audio_play_event.is_set():
            return AudioPlayerStatus.PLAYING
        else:
            return AudioPlayerStatus.PAUSED
    else:
        return AudioPlayerStatus.STOP
