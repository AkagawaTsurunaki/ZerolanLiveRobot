import asyncio

from injector import inject

from event.speech_emitter import SpeechEmitter


def syncrun(coro):
    task = [asyncio.create_task(coro)]
    asyncio.gather(*task)


class ZerolanController:

    @inject
    def __init__(self, vad: SpeechEmitter):
        self._vad = vad

    async def switch_microphone(self):
        if not self._vad.is_recording:
            await self._vad.start()
        else:
            await self._vad.stop()
