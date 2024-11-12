import numpy as np
from loguru import logger

from common.eventemitter import EventEmitter
from common.limit_list import LimitList
from common.utils.audio_util import from_ndarray_to_bytes
from services.device.microphone import Microphone
from services.vad.strategy import EasyEnergyVad


class VadEventEmitter:
    def __init__(self, emitter: EventEmitter):
        super().__init__()
        self.emitter = emitter
        self.mp = Microphone()
        self.vad = EasyEnergyVad()
        self.speech_chunks = LimitList(50)

    async def start(self):
        self.mp.open()
        await self.handler()

    def stop(self):
        self.mp.close()

    async def handler(self):
        for chunk in self.mp.stream():
            speech_chunk = np.frombuffer(chunk, dtype=np.float32)
            speech = self.vad.check_stream(speech_chunk)
            if speech is None:
                if len(self.speech_chunks) > 0:
                    combined_speech_bytes = from_ndarray_to_bytes(np.concatenate(self.speech_chunks),
                                                                  sample_rate=self.mp.sample_rate)
                    logger.info("Voice event emitted")
                    await self.emitter.emit("voice",
                                            speech=combined_speech_bytes,
                                            channels=self.mp.channels,
                                            sample_rate=self.mp.sample_rate)

                    self.speech_chunks.clear()
            else:
                self.speech_chunks.append(speech_chunk)
