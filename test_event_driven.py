import asyncio

from loguru import logger
from zerolan.data.data.asr import ASRModelStreamQuery, ASRModelPrediction
from zerolan.data.data.llm import LLMQuery, LLMPrediction

from common.eventemitter import EventEmitter
from events.vad_event import VadEventEmitter
from pipeline.asr import ASRPipeline
from pipeline.llm import LLMPipeline


class ZerolanLiveRobot:
    def __init__(self):
        self.emitter = EventEmitter()
        self.asr = ASRPipeline()
        self.llm = LLMPipeline()

    async def start(self):
        task = asyncio.create_task(self.start_emitters())
        self.test_vad()
        self.test_asr()
        self.test_llm()
        await task

    async def start_emitters(self):
        vad_emitter = VadEventEmitter(self.emitter)
        task = asyncio.create_task(vad_emitter.start())
        await task

    def test_vad(self):
        @self.emitter.on("voice")
        async def detect_voice(speech: bytes, channels: int, sample_rate: int):
            query = ASRModelStreamQuery(is_final=True, audio_data=speech, channels=channels, sample_rate=sample_rate)
            response = self.asr.stream_predict(query)
            logger.debug("asr event emitted")
            await self.emitter.emit("asr", response)

    def test_asr(self):
        @self.emitter.on("asr")
        async def asr_handler(prediction: ASRModelPrediction):
            logger.info(prediction.transcript)
            query = LLMQuery(text=prediction.transcript, history=[])
            prediction = self.llm.predict(query)
            await self.emitter.emit("llm", prediction)

    def test_llm(self):
        @self.emitter.on("llm")
        async def llm_query_handler(prediction: LLMPrediction):
            logger.info("LLM: " + prediction.response)


if __name__ == '__main__':
    bot = ZerolanLiveRobot()
    asyncio.run(bot.start())
