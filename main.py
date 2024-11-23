import threading

from PIL.Image import Image
from loguru import logger
from zerolan.data.data.asr import ASRModelStreamQuery, ASRModelPrediction
from zerolan.data.data.img_cap import ImgCapPrediction
from zerolan.data.data.llm import LLMQuery, LLMPrediction
from zerolan.data.data.ocr import OCRQuery, OCRPrediction
from zerolan.data.data.tts import TTSPrediction, TTSQuery

from agent.location_attn import LocationAttentionAgent
from agent.sentiment import SentimentAnalyzerAgent
from agent.translator import TranslatorAgent
from common.config import get_config
from common.decorator import withsound, start_ui_process, kill_ui_process
from common.enumerator import SystemSoundEnum, EventEnum, Language
from event.eventemitter import emitter
from manager.llm_prompt_manager import LLMPromptManager
from manager.temp_data_manager import TempDataManager
from manager.thread_manager import ThreadManager
from manager.tts_prompt_manager import TTSPromptManager
from pipeline.asr import ASRPipeline
from pipeline.img_cap import ImgCapPipeline
from pipeline.llm import LLMPipeline
from pipeline.ocr import OCRPipeline
from pipeline.tts import TTSPipeline
from services.browser.browser import Browser
from services.device.screen import Screen
from services.device.speaker import Speaker
from services.filter.strategy import FirstMatchedFilter
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
        self.img_cap = ImgCapPipeline(config.pipeline.img_cap)
        self.ocr = OCRPipeline(config.pipeline.ocr)

        self.speaker = Speaker()
        # [!NOTE]
        #   Here to change your live stream platform
        self.live_stream = BilibiliService(config.service.live_stream)

        # Set bad words filter
        self.filter = FirstMatchedFilter(config.character.chat.filter.bad_words)
        self.speech_manager = TTSPromptManager(config.character.speech)
        self.chat_manager = LLMPromptManager(config.character.chat)
        self.temp_data_manager = TempDataManager()
        self.thread_manager = ThreadManager()

        # Agents
        self.websocket = WebSocketServer()
        self.minecraft_agent = KonekoMinecraftAIAgent(self.websocket, config.pipeline.llm)
        self.sentiment_analyzer = SentimentAnalyzerAgent(self.speech_manager,
                                                         config.pipeline.llm)
        self.translator = TranslatorAgent(config.pipeline.llm)
        self.location_attn = LocationAttentionAgent(config.pipeline.llm)

        self.cur_lang = Language.ZH

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
            elif "游戏" in prediction.transcript:
                await self.minecraft_agent.exec_instruction(prediction.transcript)
            elif "看见" in prediction.transcript:
                img, img_save_path = Screen.capture("Edge", k=0.9)
                await emitter.emit(EventEnum.DEVICE_SCREEN_CAPTURED, img=img, img_path=img_save_path)
            elif "切换语言" in prediction.transcript:
                self.cur_lang = Language.JA
            else:
                await self.emit_llm_prediction(prediction.transcript)

        @emitter.on(EventEnum.DEVICE_SCREEN_CAPTURED)
        async def on_device_screen_captured(img: Image, img_path: str):
            # TODO: Discriminator to detect whether it includes text or image

            ocr_prediction = self.ocr.predict(OCRQuery(img_path))
            logger.info(f"OCR: {ocr_prediction.unfold_as_str()}")
            await emitter.emit(EventEnum.PIPELINE_OCR, prediction=ocr_prediction)

            # img_cap_prediction = self.img_cap.predict(ImgCapQuery(prompt="There", img_path=img_path))
            # src_lang = Language.value_of(img_cap_prediction.lang)
            # caption = self.translator.translate(src_lang, self.cur_lang, img_cap_prediction.caption)
            # img_cap_prediction.caption = caption
            # logger.info("ImgCap: " + caption)
            # await emitter.emit(EventEnum.PIPELINE_IMG_CAP, prediction=img_cap_prediction)

        @emitter.on(EventEnum.PIPELINE_OCR)
        async def on_pipeline_ocr(prediction: OCRPrediction):
            text = prediction.unfold_as_str()
            region_result = self.location_attn.find_focus(prediction.region_results)
            text = region_result.position
            await self.emit_llm_prediction(text)

        @emitter.on(EventEnum.PIPELINE_IMG_CAP)
        async def on_pipeline_img_cap(prediction: ImgCapPrediction):
            text = "你看见了" + prediction.caption
            await self.emit_llm_prediction(text)

        @emitter.on(EventEnum.PIPELINE_LLM)
        async def llm_query_handler(prediction: LLMPrediction):
            logger.info("LLM: " + prediction.response)
            tts_prompt = self.sentiment_analyzer.sentiment_tts_prompt(prediction.response)
            query = TTSQuery(
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

    async def emit_llm_prediction(self, text):
        query = LLMQuery(text=text, history=self.chat_manager.current_history)
        prediction = self.llm.predict(query)

        # Filter applied here
        is_filtered = self.filter.filter(prediction.response)
        if is_filtered:
            return

        self.chat_manager.reset_history(prediction.history)
        logger.info(f"Length of current history: {len(self.chat_manager.current_history)}")

        await emitter.emit(EventEnum.PIPELINE_LLM, prediction)

    @kill_ui_process(force=True)
    def _exit(self):
        emitter.stop()
        self.vad.stop()
        self.live_stream.stop()

    @withsound(SystemSoundEnum.exit, block=True)
    def exit(self):
        logger.info("Good bye!")
        exit(0)


if __name__ == '__main__':
    bot = ZerolanLiveRobot()
    bot.start()
    bot.exit()
