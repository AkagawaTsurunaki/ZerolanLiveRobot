import asyncio

from loguru import logger
from zerolan.data.pipeline.asr import ASRStreamQuery
from zerolan.data.pipeline.llm import LLMQuery

from common.abs_runnable import stop_all_runnable
from common.decorator import withsound
from common.enumerator import EventEnum, Language, SystemSoundEnum
from context import ZerolanLiveRobotContext
from event.event_data import ASREvent, SpeechEvent, ScreenCapturedEvent, LLMEvent
from event.eventemitter import emitter
from services.vad.emitter import VoiceEventEmitter


class ZerolanLiveRobot(ZerolanLiveRobotContext):
    def __init__(self):
        super().__init__()
        self.vad = VoiceEventEmitter()

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
        logger.info("All runnable exited.")

    @withsound(SystemSoundEnum.exit, block=True)
    def exit(self):
        logger.info("Good bye!")


async def main():
    bot = ZerolanLiveRobot()
    await bot.start()
    bot.exit()


if __name__ == '__main__':
    asyncio.run(main())
