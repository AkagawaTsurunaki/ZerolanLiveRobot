import asyncio

import pyautogui
from loguru import logger
from zerolan.data.pipeline.asr import ASRStreamQuery
from zerolan.data.pipeline.img_cap import ImgCapQuery
from zerolan.data.pipeline.llm import LLMQuery, LLMPrediction
from zerolan.data.pipeline.milvus import MilvusInsert, InsertRow, MilvusQuery
from zerolan.data.pipeline.ocr import OCRQuery
from zerolan.data.pipeline.tts import TTSQuery
from zerolan.data.pipeline.vla import ShowUiQuery
from zerolan.ump.pipeline.ocr import avg_confidence, stringify

from agent.api import find_file, sentiment_analyse, translate, summary_history, model_scale
from common.abs_runnable import stop_all_runnable
from common.data import LoadLive2DModelDTO
from common.decorator import withsound
from common.enumerator import Language, SystemSoundEnum
from common.killable_thread import kill_all_threads, KillableThread
from common.utils.audio_util import save_tmp_audio
from context import ZerolanLiveRobotContext
from event.event_data import ASREvent, SpeechEvent, ScreenCapturedEvent, LLMEvent, OCREvent, ImgCapEvent, TTSEvent, \
    QQMessageEvent, SwitchVADEvent, PlaygroundConnectedEvent
from event.eventemitter import emitter
from event.registry import EventKeyRegistry
from services.device.screen import is_image_uniform


class ZerolanLiveRobot(ZerolanLiveRobotContext):
    def __init__(self):
        super().__init__()
        self.cur_lang = Language.ZH
        self.tts_prompt_manager.set_lang(self.cur_lang)

    @withsound(SystemSoundEnum.start)
    async def start(self):
        self.init()
        threads = []

        def run_vad():
            asyncio.run(self.vad.start())

        def run_playground():
            asyncio.run(self.playground.start())

        vad_thread = KillableThread(target=run_vad, daemon=True, name="VADThread")
        threads.append(vad_thread)

        controller_thread = KillableThread(target=self.controller.run, daemon=True, name="ControllerThread")
        threads.append(controller_thread)

        if self.playground is not None:
            playground_thread = KillableThread(target=run_playground, daemon=True, name="PlaygroundThread")
            playground_thread.start()
            threads.append(playground_thread)

        controller_thread.start()
        vad_thread.start()
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(emitter.start())
                tg.create_task(self.speaker.start())
                if self.live_stream is not None:
                    tg.create_task(self.live_stream.start())

                if self.model_manager is not None:
                    tg.create_task(self.model_manager.scan())
                tg.create_task(self.webui.start())

        except ExceptionGroup as e:
            self.speaker.play_system_sound(SystemSoundEnum.error, block=False)
            logger.exception(e)
            logger.error("Unhandled exception, crashed!")
            await self._force_exit()

        for thread in threads:
            thread.join()

    def init(self):
        @emitter.on(EventKeyRegistry.Playground.PLAYGROUND_CONNECTED)
        async def on_playground_connected(_: PlaygroundConnectedEvent):
            await self.playground.load_live2d_model(
                LoadLive2DModelDTO(bot_id=self.bot_id, bot_display_name=self.bot_name, model_dir=self.live2d_model))
            logger.info(f"Live 2D model loaded: {self.live2d_model}")

        @emitter.on(EventKeyRegistry.Device.SWITCH_VAD)
        def on_open_microphone(event: SwitchVADEvent):
            if self.vad.is_recording:
                if event.switch:
                    logger.warning("The microphone has already resumed.")
                    return
                self.vad.pause()
            else:
                if not event.switch:
                    logger.warning("The microphone has already paused.")
                    return
                self.vad.resume()

        @emitter.on(EventKeyRegistry.Device.SERVICE_VAD_SPEECH_CHUNK)
        async def on_service_vad_speech_chunk(event: SpeechEvent):
            speech, channels, sample_rate = event.speech, event.channels, event.sample_rate
            query = ASRStreamQuery(is_final=True, audio_data=speech, channels=channels, sample_rate=sample_rate)
            prediction = self.asr.stream_predict(query)
            logger.info(f"ASR: {prediction.transcript}")
            logger.debug("ASREvent emitted.")
            emitter.emit(ASREvent(prediction=prediction))

        @emitter.on(EventKeyRegistry.Pipeline.ASR)
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
            elif "游戏" in prediction.transcript:
                await self.game_agent.exec_instruction(prediction.transcript)
            elif "看见" in prediction.transcript:
                img, img_save_path = self.screen.safe_capture(k=0.99)
                if not await self.check_img(img):
                    return
                emitter.emit(ScreenCapturedEvent(img=img, img_path=img_save_path))
            elif "点击" in prediction.transcript:
                img, img_save_path = self.screen.safe_capture(k=0.99)
                if not await self.check_img(img):
                    return

                query = ShowUiQuery(query=prediction.transcript, env="web", img_path=img_save_path)
                prediction = self.showui.predict(query)
                logger.debug("ShowUI: " + prediction.model_dump_json())
                action = prediction.actions[0]
                if action.action == "CLICK":
                    logger.info("Click action triggered.")
                    x, y = action.position[0] * img.width, action.position[1] * img.height
                    pyautogui.moveTo(x, y)
                    pyautogui.click()
            elif "记得" in prediction.transcript:
                query = MilvusQuery(collection_name="history_collection", limit=2, output_fields=['history', 'text'],
                                    query=prediction.transcript)
                result = self.vec_db.search(query)
                memory = result.result[0][0]
                memory = memory.entity["text"]
                logger.debug(f"Memory found: {memory}")
                await self.emit_llm_prediction(f"{memory}\n\n请根据上文回答：{prediction.transcript} \n")
            elif "加载模型" in prediction.transcript:
                file_id = find_file(self.model_manager.get_files(), prediction.transcript)
                file_info = self.model_manager.get_file_by_id(file_id)
                await self.playground.load_3d_model(file_info)
            elif "调整模型" in prediction.transcript:
                info = self.playground.get_gameobjects_info()
                if not info:
                    logger.warning("No gameobjects info")
                    return
                so = model_scale(info, prediction.transcript)
                await self.playground.modify_game_object_scale(so)
            else:
                tool_called = self.custom_agent.run(prediction.transcript)
                if not tool_called:
                    await self.emit_llm_prediction(prediction.transcript)

        @emitter.on(EventKeyRegistry.Device.SCREEN_CAPTURED)
        async def on_device_screen_captured(event: ScreenCapturedEvent):
            img, img_path = event.img, event.img_path

            ocr_prediction = self.ocr.predict(OCRQuery(img_path=img_path))
            # TODO: 0.6 is a hyperparameter that indicates the average confidence of the text contained in the image.
            if avg_confidence(ocr_prediction) > 0.6:
                logger.info("OCR: " + stringify(ocr_prediction.region_results))
                emitter.emit(OCREvent(prediction=ocr_prediction))
            else:
                img_cap_prediction = self.img_cap.predict(ImgCapQuery(prompt="There", img_path=img_path))
                src_lang = Language.value_of(img_cap_prediction.lang)
                caption = translate(src_lang, self.cur_lang, img_cap_prediction.caption)
                img_cap_prediction.caption = caption
                logger.info("ImgCap: " + caption)
                emitter.emit(ImgCapEvent(prediction=img_cap_prediction))

        @emitter.on(EventKeyRegistry.QQBot.QQ_MESSAGE)
        async def on_qq_message(event: QQMessageEvent):
            prediction = await self.emit_llm_prediction(event.message, direct_return=True)
            if prediction is None:
                logger.warning("No response from LLM remote service and will not send QQ message.")
                return
            await self.qq.send_plain_message(prediction.response, event.group_id)

        @emitter.on(EventKeyRegistry.Pipeline.OCR)
        async def on_pipeline_ocr(event: OCREvent):
            prediction = event.prediction
            text = "你看见了" + stringify(prediction.region_results) + "\n请总结一下"
            await self.emit_llm_prediction(text)

        @emitter.on(EventKeyRegistry.Pipeline.IMG_CAP)
        async def on_pipeline_img_cap(event: ImgCapEvent):
            prediction = event.prediction
            text = "你看见了" + prediction.caption
            await self.emit_llm_prediction(text)

        @emitter.on(EventKeyRegistry.Pipeline.LLM)
        async def llm_query_handler(event: LLMEvent):
            prediction = event.prediction
            text = prediction.response
            logger.info("LLM: " + text)
            sentiment = sentiment_analyse(sentiments=self.tts_prompt_manager.sentiments, text=text)
            tts_prompt = self.tts_prompt_manager.get_tts_prompt(sentiment)
            # tts_prompt = self.sentiment_analyzer_agent.sentiment_tts_prompt(text)
            if self.cur_lang == Language.ZH:
                cut_punc = "，。！？"
            elif self.cur_lang == Language.JA:
                cut_punc = "、。！？"
            else:
                cut_punc = ",.!?"

            def punc_cut(text: str, punc: str):
                texts = []
                last = -1
                for i in range(len(text)):
                    if text[i] in punc:
                        try:
                            texts.append(text[last + 1: i])
                        except IndexError:
                            continue
                        last = i
                return texts

            transcripts = punc_cut(text, cut_punc)
            for transcript in transcripts:
                query = TTSQuery(
                    text=transcript,
                    text_language=self.cur_lang,
                    refer_wav_path=tts_prompt.audio_path,
                    prompt_text=tts_prompt.prompt_text,
                    prompt_language=tts_prompt.lang,
                )
                prediction = self.tts.predict(query=query)
                await self.emit_tts_handler(TTSEvent(prediction=prediction, transcript=transcript))

    async def emit_tts_handler(self, event: TTSEvent):
        prediction = event.prediction
        if self.playground.is_playground_connected():
            bot_id = "0001"
            audio_path = save_tmp_audio(prediction.wave_data)
            await self.playground.play_speech(bot_id=bot_id, audio_path=audio_path, transcript=prediction.transcript)
        else:
            self.speaker.enqueue_sound(prediction.wave_data)

    async def emit_llm_prediction(self, text, direct_return: bool = False) -> None | LLMPrediction:
        query = LLMQuery(text=text, history=self.llm_prompt_manager.current_history)
        prediction = self.llm.predict(query)

        # Filter applied here
        is_filtered = self.filter.filter(prediction.response)
        if is_filtered:
            return
        logger.info(f"Length of current history: {len(self.llm_prompt_manager.current_history)}")
        self.llm_prompt_manager.reset_history(prediction.history, self.save_memory)
        if not direct_return:
            emitter.emit(LLMEvent(prediction=prediction))
        return prediction

    def change_lang(self, lang: Language):
        self.cur_lang = lang.name()
        self.tts_prompt_manager.set_lang(self.cur_lang)

    async def _exit(self):
        await stop_all_runnable()
        logger.info("Sent exit signal.")

    async def _force_exit(self):
        await stop_all_runnable()
        kill_all_threads()
        logger.info("Sent force-exit signal.")

    async def check_img(self, img) -> bool:
        if is_image_uniform(img):
            logger.warning("Are you sure you capture the screen properly? The screen is black!")
            await self.emit_llm_prediction("你忽然什么都看不见了！请向你的开发者求助！")
            return False
        return True

    @withsound(SystemSoundEnum.exit, block=False)
    def exit(self):
        logger.info("Good bye!")

    def save_memory(self):
        start = len(self.llm_prompt_manager.injected_history)
        history = self.llm_prompt_manager.current_history[start:]
        ai_msg = summary_history(history)
        row = InsertRow(id=1, text=ai_msg.content, subject="history")
        insert = MilvusInsert(collection_name="history_collection", texts=[row])
        insert_res = self.vec_db.insert(insert)
        if insert_res.insert_count == 1:
            logger.info(f"Add a history memory: {row.text}")
        else:
            logger.warning(f"Failed to add a history memory.")
