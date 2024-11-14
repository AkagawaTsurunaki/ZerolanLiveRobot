import asyncio
from dataclasses import dataclass

from dataclasses_json import dataclass_json
from loguru import logger
from zerolan.data.data.asr import ASRModelStreamQuery, ASRModelPrediction
from zerolan.data.data.llm import LLMQuery, LLMPrediction
from zerolan.data.data.tts import TTSQuery, TTSPrediction

from common.config import get_config
from common.decorator import withsound
from common.enum import SystemSoundEnum
from common.eventemitter import emitter
from manager.llm_prompt_manager import LLMPromptManager
from manager.temp_data_manager import TempDataManager
from manager.tts_prompt_manager import TTSPromptManager
from pipeline.asr import ASRPipeline
from pipeline.llm import LLMPipeline
from pipeline.tts import TTSPipeline
from services.browser.browser import Browser
from services.device.speaker import Speaker
from services.vad.voice_detector import VoiceDetector

config = get_config()


@dataclass_json
@dataclass
class GPT_SoVITS_TTS_Query(TTSQuery):
    cut_punc: str = "，。"


class ZerolanLiveRobot:
    def __init__(self):
        self.vad = VoiceDetector()
        self.asr = ASRPipeline(config.pipeline.asr)
        self.llm = LLMPipeline(config.pipeline.llm)
        self.tts = TTSPipeline(config.pipeline.tts)

        self.speaker = Speaker()

        self.speech_manager = TTSPromptManager(config.character.speech)
        self.chat_manager = LLMPromptManager(config.character.chat)
        self.temp_data_manager = TempDataManager()

    @withsound(SystemSoundEnum.start)
    async def start(self):
        task = asyncio.create_task(self.vad.start())
        self.register_events()
        await task

    def register_events(self):
        @emitter.on("service.vad.speech_chunk")
        async def detect_voice(speech: bytes, channels: int, sample_rate: int):
            query = ASRModelStreamQuery(is_final=True, audio_data=speech, channels=channels, sample_rate=sample_rate)
            response = self.asr.stream_predict(query)
            logger.debug("asr event emitted")
            await emitter.emit("pipeline.asr", response)

        @emitter.on("pipeline.asr")
        async def asr_handler(prediction: ASRModelPrediction):
            logger.info("ASR: " + prediction.transcript)

            if "关机" in prediction.transcript:
                self._exit()
            elif "打开浏览器" in prediction.transcript:
                self.browser = Browser(config.external_tool.browser)
                self.browser.open("https://www.bing.com")
            elif "关闭浏览器" in prediction.transcript:
                self.browser.close()
            elif "搜索" in prediction.transcript:
                self.browser.move_to_search_box()
                text = prediction.transcript[2:]
                self.browser.send_keys_and_enter(text)
            elif "错误" in prediction.transcript:
                raise Exception("Some error")
                # self.speaker.play_system_sound(SystemSoundEnum.error)
            elif "警告" in prediction.transcript:
                self.speaker.play_system_sound(SystemSoundEnum.warn)
            elif "关闭麦克风" in prediction.transcript:
                self.vad.stop()
            else:
                query = LLMQuery(text=prediction.transcript, history=self.chat_manager.current_history)
                prediction = self.llm.predict(query)
                self.chat_manager.reset_history(prediction.history)
                logger.info(f"Length of current history: {len(self.chat_manager.current_history)}")
                await emitter.emit("pipeline.llm", prediction)

        @emitter.on("pipeline.llm")
        async def llm_query_handler(prediction: LLMPrediction):
            logger.info("LLM: " + prediction.response)
            tts_prompt = self.speech_manager.default_tts_prompt
            query = GPT_SoVITS_TTS_Query(
                text=prediction.response,
                text_language="zh",
                refer_wav_path=tts_prompt.audio_path,
                prompt_text=tts_prompt.prompt_text,
                prompt_language=tts_prompt.lang,
                cut_punc="，。！",
            )
            for prediction in self.tts.stream_predict(query):
                await emitter.emit("pipeline.tts", prediction)

        @emitter.on("pipeline.llm")
        async def history_handler(prediction: LLMPrediction):
            self.chat_manager.reset_history(prediction.history)

        @emitter.on("pipeline.tts")
        async def tts_handler(prediction: TTSPrediction):
            self.speaker.playsound(prediction.wave_data, block=True)

        @emitter.on("crashed")
        @withsound(SystemSoundEnum.error, block=True)
        def crash_handler(e: Exception):
            logger.exception(e)
            logger.error("Unhandled error, crashed.")
            exit(1)

    @withsound(SystemSoundEnum.exit, block=True)
    def _exit(self):
        exit(0)

bot = ZerolanLiveRobot()

if __name__ == '__main__':
    # ui_process = Process(target=zerolan.ui.app.start_ui_application, daemon=True)
    # ui_process.start()
    asyncio.run(bot.start())
    # ui_process.kill()
    # ui_process.join()
