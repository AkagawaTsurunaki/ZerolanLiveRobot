import threading

from loguru import logger
from zerolan.data.data.asr import ASRModelStreamQuery, ASRModelPrediction
from zerolan.data.data.llm import LLMQuery, LLMPrediction
from zerolan.data.data.tts import TTSPrediction

from common.config import get_config
from common.data import GPT_SoVITS_TTS_Query
from common.decorator import withsound, start_ui_process, kill_ui_process
from common.enumerator import SystemSoundEnum, EventEnum
from event.eventemitter import emitter
from manager.llm_prompt_manager import LLMPromptManager
from manager.temp_data_manager import TempDataManager
from manager.thread_manager import ThreadManager
from manager.tts_prompt_manager import TTSPromptManager
from pipeline.asr import ASRPipeline
from pipeline.llm import LLMPipeline
from pipeline.tts import TTSPipeline
from services.browser.browser import Browser
from services.device.speaker import Speaker
from services.game.minecraft.app import KonekoMinecraftAIAgent, WebSocketServer
from services.live_stream.bilibili import BilibiliService
from services.vad.emitter import VoiceEventEmitter

config = get_config()


class ZerolanLiveRobot:
    def __init__(self):
        self.vad = VoiceEventEmitter()
        self.asr = ASRPipeline(config.pipeline.asr)
        self.llm = LLMPipeline(config.pipeline.llm)
        self.tts = TTSPipeline(config.pipeline.tts)

        self.speaker = Speaker()
        self.live_stream = BilibiliService(config.service.live_stream)
        self.websocket = WebSocketServer()
        self.minecraft_agent = KonekoMinecraftAIAgent(self.websocket, config.pipeline.llm)

        self.speech_manager = TTSPromptManager(config.character.speech)
        self.chat_manager = LLMPromptManager(config.character.chat)
        self.temp_data_manager = TempDataManager()
        self.thread_manager = ThreadManager()

    @start_ui_process(False)
    @withsound(SystemSoundEnum.start)
    def start(self):
        self.register_events()

        self.thread_manager.start_thread(threading.Thread(target=self.minecraft_agent.start, name="MinecraftAgent"))
        self.thread_manager.start_thread(threading.Thread(target=self.vad.start, name="VoiceEventEmitter"))
        self.thread_manager.start_thread(
            threading.Thread(target=self.live_stream.start, name="LiveStreamEventEmitter"))

        self.thread_manager.join_all_threads()

    def register_events(self):
        @emitter.on(EventEnum.SERVICE_VAD_SPEECH_CHUNK)
        async def detect_voice(speech: bytes, channels: int, sample_rate: int):
            query = ASRModelStreamQuery(is_final=True, audio_data=speech, channels=channels, sample_rate=sample_rate)
            response = self.asr.stream_predict(query)
            logger.debug("asr event emitted")
            await emitter.emit(EventEnum.PIPELINE_ASR, response)

        @emitter.on(EventEnum.PIPELINE_ASR)
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
                self.speaker.play_system_sound(SystemSoundEnum.error)
            elif "警告" in prediction.transcript:
                self.speaker.play_system_sound(SystemSoundEnum.warn)
            elif "关闭麦克风" in prediction.transcript:
                self.vad.stop()
            elif "测试" in prediction.transcript:
                await self.minecraft_agent.exec_instruction(prediction.transcript)
            else:
                query = LLMQuery(text=prediction.transcript, history=self.chat_manager.current_history)
                prediction = self.llm.predict(query)
                self.chat_manager.reset_history(prediction.history)
                logger.info(f"Length of current history: {len(self.chat_manager.current_history)}")
                await emitter.emit(EventEnum.PIPELINE_LLM, prediction)

        @emitter.on(EventEnum.PIPELINE_LLM)
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
                await emitter.emit(EventEnum.PIPELINE_TTS, prediction)

        @emitter.on(EventEnum.PIPELINE_LLM)
        async def history_handler(prediction: LLMPrediction):
            self.chat_manager.reset_history(prediction.history)

        @emitter.on(EventEnum.PIPELINE_TTS)
        async def tts_handler(prediction: TTSPrediction):
            self.speaker.playsound(prediction.wave_data, block=True)

        @emitter.on(EventEnum.SYSTEM_CRASHED)
        @withsound(SystemSoundEnum.error, block=False)
        def crash_handler(e: Exception):
            logger.exception(e)
            logger.error("Unhandled error, crashed.")
            self._exit()

    @kill_ui_process(force=True)
    def _exit(self):
        # emitter.stop()
        # self.vad.stop()
        # self.live_stream.stop()
        pass

    @withsound(SystemSoundEnum.exit, block=True)
    def exit(self):
        logger.info("Good bye!")
        exit(0)


if __name__ == '__main__':
    bot = ZerolanLiveRobot()
    bot.start()
    bot.exit()
