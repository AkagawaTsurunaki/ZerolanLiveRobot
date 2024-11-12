import asyncio

from loguru import logger
from zerolan.data.data.asr import ASRModelStreamQuery

from common.eventemitter import EventEmitter
from events.vad_event import VadEventEmitter
from pipeline.asr import ASRPipeline


async def test_vad():
    emitter = EventEmitter()
    ve = VadEventEmitter(emitter)
    task = asyncio.create_task(ve.start())
    pipeline = ASRPipeline()

    @emitter.on("voice")
    async def detect_voice(speech: bytes, channels: int, sample_rate: int):
        logger.info(f"Detect voice: {len(speech)}")
        query = ASRModelStreamQuery(is_final=True, audio_data=speech, channels=channels, sample_rate=sample_rate)
        response = pipeline.stream_predict(query)
        logger.info("ASR result:" + response.transcript)

    await task


if __name__ == '__main__':
    asyncio.run(test_vad())
