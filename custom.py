import asyncio

from loguru import logger
from zerolan.data.pipeline.asr import ASRStreamQuery
from zerolan.data.pipeline.img_cap import ImgCapQuery
from zerolan.data.pipeline.llm import LLMQuery
from zerolan.data.pipeline.ocr import OCRQuery
from zerolan.data.pipeline.tts import TTSQuery

from common.abs_runnable import stop_all_runnable
from common.decorator import withsound
from common.enumerator import EventEnum, Language, SystemSoundEnum
from common.thread import kill_all_threads
from context import ZerolanLiveRobotContext
from event.event_data import ASREvent, SpeechEvent, ScreenCapturedEvent, LLMEvent, OCREvent, ImgCapEvent, TTSEvent
from event.eventemitter import emitter
from pipeline.ocr import avg_confidence, stringify
from services.device.screen import is_image_uniform
from services.vad.emitter import VoiceEventEmitter


class ZerolanLiveRobot(ZerolanLiveRobotContext):
    def __init__(self):
        super().__init__()
        self.vad = VoiceEventEmitter()
        self.cur_lang = Language.ZH

    @withsound(SystemSoundEnum.start)
    async def start(self):
        self.init()
        async with asyncio.TaskGroup() as tg:
            tg.create_task(emitter.start())
            tg.create_task(self.vad.start())

    def init(self):
        @emitter.on(EventEnum.SERVICE_VAD_SPEECH_CHUNK)
        async def on_service_vad_speech_chunk(event: SpeechEvent):
            speech, channels, sample_rate = event.speech, event.channels, event.sample_rate
            query = ASRStreamQuery(is_final=True, audio_data=speech, channels=channels, sample_rate=sample_rate)
            prediction = self.asr.stream_predict(query)
            logger.info(f"ASR: {prediction.transcript}")
            logger.debug("ASREvent emitted.")
            emitter.emit(ASREvent(prediction=prediction))

        @emitter.on(EventEnum.PIPELINE_ASR)
        async def asr_handler(event: ASREvent):
            logger.debug("ASREvent received.")
            prediction = event.prediction
            if "关机" in prediction.transcript:
                await self._exit()
            elif "打开浏览器" in prediction.transcript:
                if self.browser is not None:
                    self.browser.open("https://www.bing.com")
            elif "关闭浏览器" in prediction.transcript:
                if self.browser is not None:
                    self.browser.close()
            elif "网页搜索" in prediction.transcript:
                if self.browser is not None:
                    self.browser.move_to_search_box()
                    text = prediction.transcript[4:]
                    self.browser.send_keys_and_enter(text)
            elif "关闭麦克风" in prediction.transcript:
                await self.vad.stop()
            elif "游戏" in prediction.transcript:
                await self.game_agent.exec_instruction(prediction.transcript)
            elif "看见" in prediction.transcript:
                img, img_save_path = self.screen.safe_capture(k=0.99)
                if img and img_save_path:
                    emitter.emit(ScreenCapturedEvent(img=img, img_path=img_save_path))
            elif "切换语言" in prediction.transcript:
                self.cur_lang = Language.JA
            else:
                await self.emit_llm_prediction(prediction.transcript)

        @emitter.on(EventEnum.DEVICE_SCREEN_CAPTURED)
        async def on_device_screen_captured(event: ScreenCapturedEvent):
            img, img_path = event.img, event.img_path
            if is_image_uniform(img):
                logger.warning("Are you sure you capture the screen properly? The screen is black!")
                await self.emit_llm_prediction("你忽然什么都看不见了！请向你的开发者求助！")
                return

            ocr_prediction = self.ocr.predict(OCRQuery(img_path=img_path))
            # TODO: 0.6 is a hyperparameter that indicates the average confidence of the text contained in the image.
            if avg_confidence(ocr_prediction) > 0.6:
                logger.info("OCR: " + stringify(ocr_prediction.region_results))
                emitter.emit(OCREvent(prediction=ocr_prediction))
            else:
                img_cap_prediction = self.img_cap.predict(ImgCapQuery(prompt="There", img_path=img_path))
                src_lang = Language.value_of(img_cap_prediction.lang)
                caption = self.translator_agent.translate(src_lang, self.cur_lang, img_cap_prediction.caption)
                img_cap_prediction.caption = caption
                logger.info("ImgCap: " + caption)
                emitter.emit(ImgCapEvent(prediction=img_cap_prediction))

        @emitter.on(EventEnum.PIPELINE_OCR)
        async def on_pipeline_ocr(event: OCREvent):
            prediction = event.prediction
            region_result = self.location_attention_agent.find_focus(prediction.region_results)
            text = "你看见了" + stringify(prediction.region_results) + "\n其中你最感兴趣的是\n" + region_result.content
            await self.emit_llm_prediction(text)

        @emitter.on(EventEnum.PIPELINE_IMG_CAP)
        async def on_pipeline_img_cap(event: ImgCapEvent):
            prediction = event.prediction
            text = "你看见了" + prediction.caption
            await self.emit_llm_prediction(text)

        @emitter.on(EventEnum.PIPELINE_LLM)
        async def llm_query_handler(event: LLMEvent):
            prediction = event.prediction
            logger.info("LLM: " + prediction.response)
            tts_prompt = self.sentiment_analyzer_agent.sentiment_tts_prompt(prediction.response)
            query = TTSQuery(
                text=prediction.response,
                text_language="zh",
                refer_wav_path=tts_prompt.audio_path,
                prompt_text=tts_prompt.prompt_text,
                prompt_language=tts_prompt.lang,
                cut_punc="，。！",
            )
            for prediction in self.tts.stream_predict(query):
                emitter.emit(TTSEvent(prediction=prediction))

        @emitter.on(EventEnum.PIPELINE_LLM)
        async def history_handler(event: LLMEvent):
            prediction = event.prediction
            self.llm_prompt_manager.reset_history(prediction.history)

        @emitter.on(EventEnum.PIPELINE_TTS)
        async def tts_handler(event: TTSEvent):
            prediction = event.prediction
            self.speaker.playsound(prediction.wave_data, block=True)

        @emitter.on(EventEnum.SYSTEM_CRASHED)
        @withsound(SystemSoundEnum.error, block=False)
        def crash_handler(e: Exception):
            logger.exception(e)
            logger.error("Unhandled error, crashed.")
            self._exit()

    async def emit_llm_prediction(self, text):
        query = LLMQuery(text=text, history=self.llm_prompt_manager.current_history)
        prediction = self.llm.predict(query)

        # Filter applied here
        is_filtered = self.filter.filter(prediction.response)
        if is_filtered:
            return

        self.llm_prompt_manager.reset_history(prediction.history)
        logger.info(f"Length of current history: {len(self.llm_prompt_manager.current_history)}")

        emitter.emit(LLMEvent(prediction=prediction))

    async def _exit(self):
        await stop_all_runnable()
        logger.info("Sent exit signal.")

    async def _force_exit(self):
        await stop_all_runnable()
        kill_all_threads()
        logger.info("Sent force-exit signal.")

    @withsound(SystemSoundEnum.exit, block=False)
    def exit(self):
        logger.info("Good bye!")


async def main():
    bot = ZerolanLiveRobot()
    await bot.start()
    bot.exit()


if __name__ == '__main__':
    asyncio.run(main())
