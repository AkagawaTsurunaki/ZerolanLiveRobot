import os.path
import queue
import threading
import time
from typing import List

import numpy as np
import pyaudio
from loguru import logger
from scipy.io.wavfile import write

TMP_DIR = R'.tmp\records'

CHUNK = 2 ** 12
SAMPLE_RATE = 16000
THRESHOLD = 600
MAX_MUTE_COUNT = 10

FLAG_AUDIO_RECORD = True

wave_records = queue.Queue()
wav_file_list: List[str] = []

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK
)


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
        logger.info(f"now: {energy} thr: {rec.shape[0] * THRESHOLD}")
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
        logger.info('Test in speech_recognize')
        speech = vad()
        if len(speech) != 0:
            speech = np.asarray(speech).flatten()
            logger.info('Speech detected.')

            # Write temp file for saving speech file
            tmp_wav_file_path = os.path.join(TMP_DIR, f'{time.time()}.wav')
            with open(file=tmp_wav_file_path, mode='w') as tmp_file:
                wav_file_list.append(tmp_wav_file_path)
                write(filename=tmp_file.name, rate=SAMPLE_RATE, data=speech)


def start():
    audio_record_thread = threading.Thread(target=audio_record)
    speech_recognize_thread = threading.Thread(target=save_speech)

    speech_recognize_thread.start()
    audio_record_thread.start()

    audio_record_thread.join()
    speech_recognize_thread.join()


start()
