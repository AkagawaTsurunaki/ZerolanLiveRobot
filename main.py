import threading

from PIL.Image import Image
from loguru import logger
from zerolan.data.pipeline.asr import ASRStreamQuery, ASRPrediction
from zerolan.data.pipeline.img_cap import ImgCapPrediction, ImgCapQuery
from zerolan.data.pipeline.llm import LLMQuery, LLMPrediction
from zerolan.data.pipeline.ocr import OCRQuery, OCRPrediction
from zerolan.data.pipeline.tts import TTSPrediction, TTSQuery

from agent.location_attn import LocationAttentionAgent
from agent.sentiment import SentimentAnalyzerAgent
from agent.tool_agent import ToolAgent
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
from pipeline.ocr import OCRPipeline, avg_confidence, stringify
from pipeline.tts import TTSPipeline
from services.browser.browser import Browser
from services.device.screen import Screen, is_image_uniform
from services.device.speaker import Speaker
from services.filter.strategy import FirstMatchedFilter
from services.game.minecraft.app import KonekoMinecraftAIAgent
from services.live2d.app import Live2dApplication
from services.live_stream.service import LiveStreamService
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
        if config.service.live_stream.enable:
            self.live_stream = LiveStreamService(config.service.live_stream)

        # Set bad words filter
        self.filter = FirstMatchedFilter(config.character.chat.filter.bad_words)
        self.speech_manager = TTSPromptManager(config.character.speech)
        self.chat_manager = LLMPromptManager(config.character.chat)
        self.temp_data_manager = TempDataManager()
        self.thread_manager = ThreadManager()
        self.screen = Screen()

        # Agents
        tool_agent = ToolAgent(config.pipeline.llm)
        self.minecraft_agent = KonekoMinecraftAIAgent(config.service.game, tool_agent)
        self.sentiment_analyzer = SentimentAnalyzerAgent(self.speech_manager,
                                                         config.pipeline.llm)
        self.translator = TranslatorAgent(config.pipeline.llm)
        self.location_attn = LocationAttentionAgent(config.pipeline.llm)
        self.live2d = Live2dApplication(config.service.live2d)

        self.cur_lang = Language.ZH

    @start_ui_process(False)
    @withsound(SystemSoundEnum.start)
    def start(self):
        self.register_events()

        self.thread_manager.start_thread(threading.Thread(target=self.minecraft_agent.start, name="MinecraftAgent"))
        self.thread_manager.start_thread(threading.Thread(target=self.vad.start, name="VoiceEventEmitter"))
        if config.service.live_stream.enable:
            self.thread_manager.start_thread(
                threading.Thread(target=self.live_stream.start, name="LiveStreamEventEmitter"))
        self.thread_manager.start_thread(threading.Thread(target=self.live2d.start, name="Live2dApplication"))

        self.thread_manager.join_all_threads()

    def register_events(self):
        @emitter.on(EventEnum.SERVICE_VAD_SPEECH_CHUNK)
        async def detect_voice(speech: bytes, channels: int, sample_rate: int):
            query = ASRStreamQuery(is_final=True, audio_data=speech, channels=channels, sample_rate=sample_rate)
            response = self.asr.stream_predict(query)
            logger.debug("asr event emitted")
            await emitter.emit(EventEnum.PIPELINE_ASR, response)

        @emitter.on(EventEnum.PIPELINE_ASR)
        async def asr_handler(prediction: ASRPrediction):
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
            elif "关闭麦克风" in prediction.transcript:
                self.vad.stop()
            elif "游戏" in prediction.transcript:
                await self.minecraft_agent.exec_instruction(prediction.transcript)
            elif "看见" in prediction.transcript:
                img, img_save_path = self.screen.safe_capture(k=0.99)
                if img and img_save_path:
                    await emitter.emit(EventEnum.DEVICE_SCREEN_CAPTURED, img=img, img_path=img_save_path)
            elif "切换语言" in prediction.transcript:
                self.cur_lang = Language.JA
            else:
                await self.emit_llm_prediction(prediction.transcript)

        @emitter.on(EventEnum.DEVICE_SCREEN_CAPTURED)
        async def on_device_screen_captured(img: Image, img_path: str):
            if is_image_uniform(img):
                logger.warning("Are you sure you capture the screen properly? The screen is black!")
                await self.emit_llm_prediction("你忽然什么都看不见了！请向你的开发者求助！")
                return

            ocr_prediction = self.ocr.predict(OCRQuery(img_path=img_path))
            # TODO: 0.6 is a hyperparameter that indicates the average confidence of the text contained in the image.
            if avg_confidence(ocr_prediction) > 0.6:
                logger.info("OCR: " + stringify(ocr_prediction.region_results))
                await emitter.emit(EventEnum.PIPELINE_OCR, prediction=ocr_prediction)
            else:
                img_cap_prediction = self.img_cap.predict(ImgCapQuery(prompt="There", img_path=img_path))
                src_lang = Language.value_of(img_cap_prediction.lang)
                caption = self.translator.translate(src_lang, self.cur_lang, img_cap_prediction.caption)
                img_cap_prediction.caption = caption
                logger.info("ImgCap: " + caption)
                await emitter.emit(EventEnum.PIPELINE_IMG_CAP, prediction=img_cap_prediction)

        @emitter.on(EventEnum.PIPELINE_OCR)
        async def on_pipeline_ocr(prediction: OCRPrediction):
            region_result = self.location_attn.find_focus(prediction.region_results)
            text = "你看见了" + stringify(prediction.region_results) + "\n其中你最感兴趣的是\n" + region_result.content
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
        self.minecraft_agent.stop()
        self.vad.stop()
        self.live_stream.stop()
        self.live2d.stop()

    @withsound(SystemSoundEnum.exit, block=True)
    def exit(self):
        logger.info("Good bye!")
        exit(0)


if __name__ == '__main__':
    bot = ZerolanLiveRobot()
    bot.start()
    bot.exit()
