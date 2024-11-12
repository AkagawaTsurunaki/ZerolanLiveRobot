import asyncio

from loguru import logger
from zerolan.data.data.asr import ASRModelStreamQuery

from common.eventemitter import EventEmitter
from events.vad_event import VadEventEmitter
from pipeline.asr import ASRPipeline


class ZerolanLiveRobot:
    def __init__(self):
        self.emitter = EventEmitter()
        self.asr = ASRPipeline()

    async def start(self):
        task = asyncio.create_task(self.start_emitters())
        task2 = asyncio.create_task(self.test_vad())
        await task
        await task2

    async def start_emitters(self):
        vad_emitter = VadEventEmitter(self.emitter)
        task = asyncio.create_task(vad_emitter.start())
        await task


    async def test_vad(self):
        @self.emitter.on("voice")
        def detect_voice(speech: bytes, channels: int, sample_rate: int):
            query = ASRModelStreamQuery(is_final=True, audio_data=speech, channels=channels, sample_rate=sample_rate)
            response = self.asr.stream_predict(query)
            logger.debug(response.transcript)


if __name__ == '__main__':
    bot = ZerolanLiveRobot()
    asyncio.run(bot.start())
