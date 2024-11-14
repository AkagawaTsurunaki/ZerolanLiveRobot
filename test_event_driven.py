import asyncio
from dataclasses import dataclass

from dataclasses_json import dataclass_json
from loguru import logger
from zerolan.data.data.asr import ASRModelStreamQuery, ASRModelPrediction
from zerolan.data.data.llm import LLMQuery, LLMPrediction
from zerolan.data.data.tts import TTSQuery, TTSPrediction

from common.config import get_config
from common.enum import SystemSoundEnum
from common.eventemitter import EventEmitter
from events.vad_event import VadEventEmitter
from manager.llm_prompt_manager import LLMPromptManager
from manager.tts_prompt_manager import TTSPromptManager
from pipeline.asr import ASRPipeline
from pipeline.llm import LLMPipeline
from pipeline.tts import TTSPipeline
from services.device.speaker import Speaker

config = get_config()


@dataclass_json
@dataclass
class GPT_SoVITS_TTS_Query(TTSQuery):
    cut_punc: str = "，。"


class ZerolanLiveRobot:
    def __init__(self):
        self.emitter = EventEmitter()
        self.asr = ASRPipeline(config.pipeline.asr)
        self.llm = LLMPipeline(config.pipeline.llm)
        self.tts = TTSPipeline(config.pipeline.tts)

        self.speaker = Speaker()

        self.speech_manager = TTSPromptManager(config.character.speech)
        self.chat_manager = LLMPromptManager(config.character.chat)

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
            query = LLMQuery(text=prediction.transcript, history=self.chat_manager.current_history)
            prediction = self.llm.predict(query)
            self.chat_manager.reset_history(prediction.history)
            logger.info(f"Length of current history: {len(self.chat_manager.current_history)}")
            await self.emitter.emit("llm", prediction)

        @self.emitter.on("asr")
        async def command_handler(prediction: ASRModelPrediction):
            if "关机" in prediction.transcript:
                self.speaker.play_system_sound(SystemSoundEnum.exit)
                logger.debug("Simulate exit")

    def on_llm(self):
        @self.emitter.on("llm")
        async def llm_query_handler(prediction: LLMPrediction):
            logger.info("LLM: " + prediction.response)
            tts_prompt = self.speech_manager.default_tts_prompt
            query = TTSQuery(
                text=prediction.response,
                text_language="zh",
                refer_wav_path=tts_prompt.audio_path,
                prompt_text=tts_prompt.prompt_text,
                prompt_language=tts_prompt.lang,
            )
            for prediction in self.tts.stream_predict(query):
                await self.emitter.emit("tts", prediction)

        @self.emitter.on("llm")
        async def history_handler(prediction: LLMPrediction):
            self.chat_manager.reset_history(prediction.history)

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
