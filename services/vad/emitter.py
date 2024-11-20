import asyncio

import numpy as np
from loguru import logger

from common.decorator import withsound
from common.enumerator import SystemSoundEnum, EventEnum
from event.eventemitter import emitter
from common.limit_list import LimitList
from common.utils.audio_util import from_ndarray_to_bytes
from services.device.microphone import Microphone
from services.vad.strategy import EasyEnergyVad


class VoiceEventEmitter:
    def __init__(self):
        super().__init__()
        self.mp = Microphone()
        self.vad = EasyEnergyVad()
        self.speech_chunks = LimitList(50)
        self._stop_flag = False

    @withsound(SystemSoundEnum.enable_func)
    def start(self):
        self.mp.open()
        asyncio.run(self.handler())

    @withsound(SystemSoundEnum.disable_func)
    def stop(self):
        self._stop_flag = True
        self.mp.close()

    async def handler(self):
        for chunk in self.mp.stream():
            if self._stop_flag:
                break
            speech_chunk = np.frombuffer(chunk, dtype=np.float32)
            speech = self.vad.check_stream(speech_chunk)
            if speech is None:
                if len(self.speech_chunks) > 0:
                    combined_speech_bytes = from_ndarray_to_bytes(np.concatenate(self.speech_chunks),
                                                                  sample_rate=self.mp.sample_rate)
                    logger.info("Voice event emitted")
                    await emitter.emit(EventEnum.SERVICE_VAD_SPEECH_CHUNK,
                                       speech=combined_speech_bytes,
                                       channels=self.mp.channels,
                                       sample_rate=self.mp.sample_rate)

                    self.speech_chunks.clear()
            else:
                self.speech_chunks.append(speech_chunk)
