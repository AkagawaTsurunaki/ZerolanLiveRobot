import os.path
import queue
import sys
import threading
import time
from dataclasses import dataclass
from os import PathLike
from typing import List

import numpy as np
import pyaudio
from loguru import logger
from scipy.io.wavfile import write

logger.remove()
logger.add(sys.stderr, level="INFO")

SAVE_DIR = R'.tmp\records'

CHUNK = 2 ** 12
SAMPLE_RATE = 16000
THRESHOLD = 600
MAX_MUTE_COUNT = 10

FLAG_AUDIO_RECORD = True


@dataclass
class WavFile:
    is_read: bool
    wav_file_path: str


wave_records = queue.Queue()
wav_file_list: List[WavFile] = []
stream: pyaudio.Stream


def init(save_dir: str | PathLike, chunk: int, sample_rate: int, threshold: int, max_mute_count: int):
    global stream, SAVE_DIR, CHUNK, SAMPLE_RATE, THRESHOLD, MAX_MUTE_COUNT
    SAVE_DIR = save_dir
    CHUNK = chunk
    SAMPLE_RATE = sample_rate
    THRESHOLD = threshold
    MAX_MUTE_COUNT = max_mute_count
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK
    )
    return True


def audio_record():
    while FLAG_AUDIO_RECORD:
        data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
        wave_records.put(data)


def vad():
    ret = []
    mute_count = 0
    while mute_count < MAX_MUTE_COUNT:
        rec = wave_records.get()
        energy = np.sum(np.abs(rec))
        ret.append(rec)
        logger.debug(f"now: {energy} thr: {rec.shape[0] * THRESHOLD}")
        if energy < rec.shape[0] * THRESHOLD:
            mute_count += 1
        else:
            mute_count = 0

    is_speech = False

    for rec in ret:
        if np.sum(np.abs(rec)) > rec.shape[0] * THRESHOLD:
            is_speech = True

    ret = ret if is_speech else []
    return ret


def save_speech():
    """
    检测是否有人在说话
    """
    while True:
        speech = vad()
        if len(speech) != 0:
            speech = np.asarray(speech).flatten()
            logger.info('VAD 激活')

            # Write temp file for saving speech file
            tmp_wav_file_path = os.path.join(SAVE_DIR, f'{time.time()}.wav')
            with open(file=tmp_wav_file_path, mode='w') as tmp_file:
                wav_file_list.append(WavFile(wav_file_path=tmp_wav_file_path, is_read=False))
                write(filename=tmp_file.name, rate=SAMPLE_RATE, data=speech)


def select01():
    if len(wav_file_list) > 0:
        unread_wav_list = [wav_file for wav_file in wav_file_list if not wav_file.is_read]
        if len(unread_wav_list) > 0:
            unread_wav_file = unread_wav_list[-1]
            unread_wav_file.is_read = True
            return unread_wav_file.wav_file_path
    return None


def start():
    audio_record_thread = threading.Thread(target=audio_record)
    speech_recognize_thread = threading.Thread(target=save_speech)

    speech_recognize_thread.start()
    audio_record_thread.start()

    logger.info('VAD 服务已启动')

    audio_record_thread.join()
    speech_recognize_thread.join()
