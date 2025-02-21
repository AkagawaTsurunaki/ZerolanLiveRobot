import asyncio
import threading

import numpy as np
from loguru import logger

from common.abs_runnable import AbstractRunnable
from common.decorator import withsound
from common.enumerator import SystemSoundEnum
from common.limit_list import LimitList
from common.utils.audio_util import from_ndarray_to_bytes
from event.event_data import SpeechEvent
from event.eventemitter import emitter
from services.device.microphone import Microphone
from services.vad.strategy import EasyEnergyVad


class SpeechEmitter(AbstractRunnable):
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

    async def start(self):
        await super().start()
        self._stop_flag = False
        self.mp.open()
        await self.handler()

    @withsound(SystemSoundEnum.enable_func)
    def resume(self):
        self._pause_event.set()
        self._stop_flag = False
        logger.info("VAD resumed.")

    async def stop(self):
        await super().stop()
        self._stop_flag = True
        self.mp.close()

    @withsound(SystemSoundEnum.disable_func)
    def pause(self):
        self._pause_event.clear()
        self._stop_flag = True
        logger.info("VAD paused.")

    async def handler(self):
        for chunk in self.mp.stream():
            logger.debug("Test")
            if self._stop_flag:
                logger.debug("Microphone `_pause_event` clear.")
                await asyncio.sleep(0)
                # └---- ⚠️ 【警告】
                #           不要删除上方的这行代码，否则关闭麦克风时将会产生段错误：-1073741819(0xC0000005)
                #           初步判断可能是协程实现的问题
                #           使用日志 IO 和显式 asyncio.sleep(0) 可以强制挂起本任务，让出任务执行权
                self._pause_event.wait()
                logger.debug("Microphone `_pause_event` set")

            await asyncio.sleep(0)
            speech_chunk = np.frombuffer(chunk, dtype=np.float32)
            speech = self.vad.check_stream(speech_chunk)
            if speech is None:
                if len(self.speech_chunks) > 0:
                    combined_speech_bytes = from_ndarray_to_bytes(np.concatenate(self.speech_chunks),
                                                                  sample_rate=self.mp.sample_rate)
                    logger.info("Voice event emitted")
                    emitter.emit(SpeechEvent(speech=combined_speech_bytes,
                                             channels=self.mp.channels,
                                             sample_rate=self.mp.sample_rate))

                    self.speech_chunks.clear()
            else:
                self.speech_chunks.append(speech_chunk)
