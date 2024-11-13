import asyncio
from copy import deepcopy
from dataclasses import dataclass

from dataclasses_json import dataclass_json
from loguru import logger
from zerolan.data.data.asr import ASRModelStreamQuery, ASRModelPrediction
from zerolan.data.data.llm import LLMQuery, LLMPrediction
from zerolan.data.data.tts import TTSQuery, TTSPrediction

from common.eventemitter import EventEmitter
from events.vad_event import VadEventEmitter
from pipeline.asr import ASRPipeline
from pipeline.llm import LLMPipeline
from pipeline.tts import TTSPipeline
from services.device.speaker import Speaker


@dataclass_json
@dataclass
class GPT_SoVITS_TTS_Query(TTSQuery):
    cut_punc: str = "，。"


default_tts_query = GPT_SoVITS_TTS_Query(
    text="",
    text_language="zh",
    refer_wav_path=R"D:\AkagawaTsurunaki\WorkSpace\PythonProjects\ZerolanLiveRobot\resources\static\audio\momoi\[zh][正常]喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？.wav",
    prompt_text="喜欢游戏的人和擅长游戏的人有很多不一样的地方，老师属于哪一种呢？",
    prompt_language="zh",
    cut_punc="，。")


class ZerolanLiveRobot:
    def __init__(self):
        self.emitter = EventEmitter()
        self.asr = ASRPipeline()
        self.llm = LLMPipeline()
        self.tts = TTSPipeline()

        self.speaker = Speaker()

        self.history = []

    async def start(self):
        task = asyncio.create_task(self.start_emitters())
        self.on_voice()
        self.on_asr()
        self.on_llm()
        self.on_tts()
        await task

    async def start_emitters(self):
        vad_emitter = VadEventEmitter(self.emitter)
        task = asyncio.create_task(vad_emitter.start())
        await task

    def on_voice(self):
        @self.emitter.on("voice")
        async def detect_voice(speech: bytes, channels: int, sample_rate: int):
            query = ASRModelStreamQuery(is_final=True, audio_data=speech, channels=channels, sample_rate=sample_rate)
            response = self.asr.stream_predict(query)
            logger.debug("asr event emitted")
            await self.emitter.emit("asr", response)

    def on_asr(self):
        @self.emitter.on("asr")
        async def asr_handler(prediction: ASRModelPrediction):
            logger.info(prediction.transcript)
            query = LLMQuery(text=prediction.transcript, history=[])
            prediction = self.llm.predict(query)
            await self.emitter.emit("llm", prediction)

        @self.emitter.on("asr")
        async def command_handler(prediction: ASRModelPrediction):
            if "关机" in prediction.transcript:
                exit()


    def on_llm(self):
        @self.emitter.on("llm")
        async def llm_query_handler(prediction: LLMPrediction):
            logger.info("LLM: " + prediction.response)
            query = deepcopy(default_tts_query)
            query.text = prediction.response
            for prediction in self.tts.stream_predict(query):
                await self.emitter.emit("tts", prediction)

    def on_tts(self):
        @self.emitter.on("tts")
        async def tts_handler(prediction: TTSPrediction):
            self.speaker.playsound(prediction.wave_data, block=True)

    def on_open(self):
        # @self.emitter.on("cnm")
        ...

if __name__ == '__main__':
    bot = ZerolanLiveRobot()
    asyncio.run(bot.start())
