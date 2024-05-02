import os
import queue
import sys
import threading
import time
from typing import List

import numpy as np
import pyaudio
import scipy
from loguru import logger

from common.datacls import WavFile, VADServiceStatus
from common.exc import InitError
from config import GLOBAL_CONFIG as G_CFG

logger.remove()
logger.add(sys.stderr, level="INFO")

_save_dir: str
_chunk: int
_sample_rate: int
_threshold: int
_max_mute_count: int
_stream: pyaudio.Stream
_record_speech_in_loop_event: threading.Event
_wave_records: queue.Queue
_g_wav_file_list: List[WavFile]
_running: bool


def init():
    global _save_dir, _chunk, _save_dir, _sample_rate, _threshold, _max_mute_count, _stream, _record_speech_in_loop_event, _wave_records, _g_wav_file_list, _running

    _save_dir = G_CFG.voice_activity_detection.save_dir
    _chunk = G_CFG.voice_activity_detection.chunk
    _sample_rate = G_CFG.voice_activity_detection.sample_rate
    _threshold = G_CFG.voice_activity_detection.threshold
    _max_mute_count = G_CFG.voice_activity_detection.max_mute_count
    try:
        _stream = pyaudio.PyAudio().open(
            format=pyaudio.paInt16, channels=1, rate=_sample_rate, input=True, frames_per_buffer=_chunk
        )
    except OSError as e:
        if e.errno == -9996:
            raise InitError('Input device unavailable: Maybe you did not give the microphone permission.')

    # Record speech in loop event
    _record_speech_in_loop_event = threading.Event()

    _wave_records = queue.Queue()
    _g_wav_file_list = []

    _running = False


def start():
    audio_record_thread = threading.Thread(target=record_speech_in_loop)
    speech_recognize_thread = threading.Thread(target=save_speech_in_loop)
    _record_speech_in_loop_event.set()

    speech_recognize_thread.start()
    audio_record_thread.start()

    logger.info('VAD service started.')

    audio_record_thread.join()
    speech_recognize_thread.join()


def stop():
    global _running
    _running = False
    _record_speech_in_loop_event.clear()
    logger.warning('VAD Service stopped.')


def pause():
    if _record_speech_in_loop_event.is_set():
        _record_speech_in_loop_event.clear()
        logger.info('VAD service paused.')
    else:
        logger.warning('Invalid operation: VAD service has been paused.')


def resume():
    if not _record_speech_in_loop_event.is_set():
        _record_speech_in_loop_event.set()
        logger.info('🎙️ VAD 服务继续')
    else:
        logger.warning('Invalid operation: VAD service has been resumed.')


def status() -> VADServiceStatus:
    if _running:
        if _record_speech_in_loop_event.is_set():
            return VADServiceStatus.RECORDING
        else:
            return VADServiceStatus.PAUSED
    else:
        return VADServiceStatus.STOP


def record_speech_in_loop():
    while _running:
        _record_speech_in_loop_event.wait()
        data = np.fromstring(_stream.read(_chunk), dtype=np.int16)
        _wave_records.put(data)


def save_speech_in_loop():
    """
    Detect whether voice exists.
    """
    while _running:
        _record_speech_in_loop_event.wait()
        speech = vad()
        if len(speech) != 0:
            speech = np.asarray(speech).flatten()
            logger.info('VAD activated!')

            # Write temp file for saving speech file
            tmp_wav_file_path = os.path.join(_save_dir, f'{time.time()}.wav')
            with open(file=tmp_wav_file_path, mode='w') as tmp_file:
                _g_wav_file_list.append(WavFile(wav_file_path=tmp_wav_file_path, is_read=False))
                scipy.io.wavfile.write(filename=tmp_file.name, rate=_sample_rate, data=speech)


def vad():
    ret = []
    mute_count = 0
    while mute_count < _max_mute_count:
        rec = _wave_records.get()
        energy = np.sum(np.abs(rec))
        ret.append(rec)
        logger.debug(f"now: {energy} thr: {rec.shape[0] * _threshold}")
        if energy < rec.shape[0] * _threshold:
            mute_count += 1
        else:
            mute_count = 0

    is_speech = False

    for rec in ret:
        if np.sum(np.abs(rec)) > rec.shape[0] * _threshold:
            is_speech = True

    ret = ret if is_speech else []
    return ret


def select_latest_unread():
    if len(_g_wav_file_list) > 0:
        unread_wav_list = [wav_file for wav_file in _g_wav_file_list if not wav_file.is_read]
        if len(unread_wav_list) > 0:
            for item in _g_wav_file_list:
                item.is_read = True
            unread_wav_file = unread_wav_list[-1]
            return unread_wav_file.wav_file_path
    return None
