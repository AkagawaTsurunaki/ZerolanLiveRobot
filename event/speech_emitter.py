import threading

import numpy as np
from loguru import logger

from common.abs_runnable import ThreadRunnable
from services.device.speaker import withsound, SystemSoundEnum
from common.limit_list import LimitList
from common.utils.audio_util import from_ndarray_to_bytes
from event.event_data import SpeechEvent
from event.event_emitter import emitter
from services.device.microphone import Microphone
from services.vad.strategy import EasyEnergyVad


class SpeechEmitter(ThreadRunnable):
    def name(self):
        return "VoiceEventEmitter"

    def __init__(self, microphone: Microphone):
        super().__init__()
        self.mp = microphone
        self.vad = EasyEnergyVad()
        self.speech_chunks = LimitList(50)
        self._stop_flag = False
        self._pause_event = threading.Event()

    @property
    def is_recording(self):
        return not self._stop_flag

    def start(self):
        super().start()
        self._stop_flag = False
        self.mp.open()
        self.handler()

    @withsound(SystemSoundEnum.enable_func)
    def resume(self):
        self._pause_event.set()
        self._stop_flag = False
        logger.info("VAD resumed.")

    def stop(self):
        super().stop()
        self._stop_flag = True
        self.mp.close()

    @withsound(SystemSoundEnum.disable_func)
    def pause(self):
        self._pause_event.clear()
        self._stop_flag = True
        logger.info("VAD paused.")

    def handler(self):
        for chunk in self.mp.stream():
            # print("-^v-", end="")
            if self._stop_flag:
                logger.debug("Microphone `_pause_event` clear.")
                self._pause_event.wait()
                logger.debug("Microphone `_pause_event` set")

            speech_chunk = np.frombuffer(chunk, dtype=np.float32)
            speech = self.vad.check_stream(speech_chunk)
            if speech is None:
                if len(self.speech_chunks) > 0:
                    combined_speech_bytes = from_ndarray_to_bytes(np.concatenate(self.speech_chunks),
                                                                  sample_rate=self.mp.sample_rate)
                    logger.info("Voice event emitted")
                    emitter.emit(SpeechEvent(speech=combined_speech_bytes,
                                             channels=self.mp.channels,
                                             sample_rate=self.mp.sample_rate,
                                             audio_type='raw'))

                    self.speech_chunks.clear()
            else:
                self.speech_chunks.append(speech_chunk)
