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
from utils.util import save

logger.remove()
logger.add(sys.stderr, level="INFO")

SAVE_DIR = R'.tmp\records'

CHUNK = 2 ** 12
SAMPLE_RATE = 16000
THRESHOLD = 600
MAX_MUTE_COUNT = 10

# 循环存储语音文件线程等待事件
save_speech_in_loop_event = threading.Event()
# 循环录音线程等待事件
record_speech_in_loop_event = threading.Event()


@dataclass
class WavFile:
    is_read: bool
    wav_file_path: str


wave_records = queue.Queue()
g_wav_file_list: List[WavFile] = []
stream: pyaudio.Stream


def init(save_dir: str | PathLike, chunk: int, sample_rate: int, threshold: int, max_mute_count: int):
    logger.info('🎙️ VAD 服务初始化中……')
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
    logger.info('🎙️ VAD 服务初始化完毕')
    return True


def record_speech_in_loop():
    while True:
        # 线程等待如果没有开启记录
        record_speech_in_loop_event.wait()
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


def save_speech_in_loop():
    """
    检测是否有人在说话
    """
    while True:
        record_speech_in_loop_event.wait()
        speech = vad()
        if len(speech) != 0:
            speech = np.asarray(speech).flatten()
            logger.info('🎙️ VAD 激活')

            # Write temp file for saving speech file
            tmp_wav_file_path = os.path.join(SAVE_DIR, f'{time.time()}.wav')
            with open(file=tmp_wav_file_path, mode='w') as tmp_file:
                g_wav_file_list.append(WavFile(wav_file_path=tmp_wav_file_path, is_read=False))
                write(filename=tmp_file.name, rate=SAMPLE_RATE, data=speech)


def select_latest_unread():
    if len(g_wav_file_list) > 0:
        unread_wav_list = [wav_file for wav_file in g_wav_file_list if not wav_file.is_read]
        if len(unread_wav_list) > 0:
            for item in g_wav_file_list:
                item.is_read = True
            unread_wav_file = unread_wav_list[-1]
            return unread_wav_file.wav_file_path
    return None


def switch() -> bool:
    if record_speech_in_loop_event.is_set():
        record_speech_in_loop_event.clear()
        save_speech_in_loop_event.clear()
        logger.info('🎙️ VAD 服务暂停')
        return False
    else:
        record_speech_in_loop_event.set()
        save_speech_in_loop_event.set()
        logger.info('🎙️ VAD 服务继续')
        return True


def start():
    audio_record_thread = threading.Thread(target=record_speech_in_loop)
    speech_recognize_thread = threading.Thread(target=save_speech_in_loop)

    record_speech_in_loop_event.set()
    save_speech_in_loop_event.set()

    speech_recognize_thread.start()
    audio_record_thread.start()

    logger.info('🎙️ VAD 服务已启动')

    audio_record_thread.join()
    speech_recognize_thread.join()
