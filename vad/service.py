import os
import queue
import sys
import threading
import time
from dataclasses import dataclass
from typing import List

import numpy as np
import pyaudio
import scipy
from loguru import logger

from common.abs_service import AbstractService, ServiceStatus
from config import GlobalConfig
from common.datacls import WavFile

logger.remove()
logger.add(sys.stderr, level="INFO")


@dataclass
class VADServiceStatus(ServiceStatus):
    RECORDING = 'RECORDING'
    PAUSED = 'PAUSED'
    STOP = 'STOP'


class VADService(AbstractService):
    def __init__(self, cfg: GlobalConfig):
        self._save_dir: str = cfg.voice_activity_detection.save_dir
        self._chunk: int = cfg.voice_activity_detection.chunk
        self._sample_rate: int = cfg.voice_activity_detection.sample_rate
        self._threshold: int = cfg.voice_activity_detection.threshold
        self._max_mute_count: int = cfg.voice_activity_detection.max_mute_count
        self._stream = pyaudio.PyAudio().open(
            format=pyaudio.paInt16, channels=1, rate=self._sample_rate, input=True, frames_per_buffer=self._chunk
        )

        # Record speech in loop event
        self._record_speech_in_loop_event = threading.Event()

        self._wave_records = queue.Queue()
        self._g_wav_file_list: List[WavFile] = []

        self._running = False

    def start(self):
        audio_record_thread = threading.Thread(target=self.record_speech_in_loop)
        speech_recognize_thread = threading.Thread(target=self.save_speech_in_loop)
        self._record_speech_in_loop_event.set()

        speech_recognize_thread.start()
        audio_record_thread.start()

        logger.info('VAD service started.')

        audio_record_thread.join()
        speech_recognize_thread.join()

    def stop(self):
        self._running = False
        self._record_speech_in_loop_event.clear()
        logger.warning('VAD Service stopped.')

    def pause(self):
        if self._record_speech_in_loop_event.is_set():
            self._record_speech_in_loop_event.clear()
            logger.info('VAD service paused.')
        else:
            logger.warning('Invalid operation: VAD service has been paused.')

    def resume(self):
        if not self._record_speech_in_loop_event.is_set():
            self._record_speech_in_loop_event.set()
            logger.info('🎙️ VAD 服务继续')
        else:
            logger.warning('Invalid operation: VAD service has been resumed.')

    def status(self) -> VADServiceStatus:
        if self._running:
            if self._record_speech_in_loop_event.is_set():
                return VADServiceStatus.RECORDING
            else:
                return VADServiceStatus.PAUSED
        else:
            return VADServiceStatus.STOP

    def record_speech_in_loop(self):
        while self._running:
            self._record_speech_in_loop_event.wait()
            data = np.fromstring(self._stream.read(self._chunk), dtype=np.int16)
            self._wave_records.put(data)

    def save_speech_in_loop(self):
        """
        Detect whether voice exists.
        """
        while self._running:
            self._record_speech_in_loop_event.wait()
            speech = self.vad()
            if len(speech) != 0:
                speech = np.asarray(speech).flatten()
                logger.info('VAD activated!')

                # Write temp file for saving speech file
                tmp_wav_file_path = os.path.join(self._save_dir, f'{time.time()}.wav')
                with open(file=tmp_wav_file_path, mode='w') as tmp_file:
                    self._g_wav_file_list.append(WavFile(wav_file_path=tmp_wav_file_path, is_read=False))
                    scipy.io.wavfile.write(filename=tmp_file.name, rate=self._sample_rate, data=speech)

    def vad(self):
        ret = []
        mute_count = 0
        while mute_count < self._max_mute_count:
            rec = self._wave_records.get()
            energy = np.sum(np.abs(rec))
            ret.append(rec)
            logger.debug(f"now: {energy} thr: {rec.shape[0] * self._threshold}")
            if energy < rec.shape[0] * self._threshold:
                mute_count += 1
            else:
                mute_count = 0

        is_speech = False

        for rec in ret:
            if np.sum(np.abs(rec)) > rec.shape[0] * self._threshold:
                is_speech = True

        ret = ret if is_speech else []
        return ret

    def select_latest_unread(self):
        if len(self._g_wav_file_list) > 0:
            unread_wav_list = [wav_file for wav_file in self._g_wav_file_list if not wav_file.is_read]
            if len(unread_wav_list) > 0:
                for item in self._g_wav_file_list:
                    item.is_read = True
                unread_wav_file = unread_wav_list[-1]
                return unread_wav_file.wav_file_path
        return None
