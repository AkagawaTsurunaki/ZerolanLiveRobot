import asyncio

from loguru import logger
from zerolan.data.pipeline.asr import ASRStreamQuery

from common.enumerator import EventEnum
from context import ZerolanLiveRobotContext
from event.event_data import ASREvent, SpeechEvent
from event.eventemitter import emitter
from services.vad.emitter import VoiceEventEmitter


class ZerolanLiveRobot(ZerolanLiveRobotContext):
    def __init__(self):
        super().__init__()
        self.vad = VoiceEventEmitter()

    async def start(self):
        self.init()
        async with asyncio.TaskGroup() as tg:
            tg.create_task(emitter.start())
            tg.create_task(self.vad.astart())

    def init(self):
        @emitter.on(EventEnum.SERVICE_VAD_SPEECH_CHUNK)
        async def detect_voice(event: SpeechEvent):
            speech, channels, sample_rate = event.speech, event.channels, event.sample_rate
            query = ASRStreamQuery(is_final=True, audio_data=speech, channels=channels, sample_rate=sample_rate)
            prediction = self.asr.stream_predict(query)
            logger.info("ASR: " + prediction.transcript)
            await emitter.emit(ASREvent(prediction=prediction))


async def main():
    bot = ZerolanLiveRobot()
    await bot.start()


if __name__ == '__main__':
    asyncio.run(main())
