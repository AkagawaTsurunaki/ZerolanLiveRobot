import asyncio
import os
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path

from loguru import logger
from zerolan.data.data.prompt import TTSPrompt
from zerolan.data.pipeline.asr import ASRStreamQuery
from zerolan.data.pipeline.img_cap import ImgCapQuery
from zerolan.data.pipeline.llm import LLMQuery, LLMPrediction
from zerolan.data.pipeline.milvus import MilvusInsert, InsertRow, MilvusQuery
from zerolan.data.pipeline.ocr import OCRQuery
from zerolan.data.pipeline.tts import TTSQuery
from zerolan.data.pipeline.vla import ShowUiQuery

from agent.api import sentiment_analyse, translate, summary_history, find_file, model_scale
from common.concurrent.abs_runnable import stop_all_runnable
from common.concurrent.killable_thread import KillableThread, kill_all_threads
from common.enumerator import Language
from common.io.api import save_audio
from common.io.file_type import AudioFileType
from common.utils import audio_util, math_util
from common.utils.img_util import is_image_uniform
from common.utils.str_util import split_by_punc
from context import ZerolanLiveRobotContext
from event.event_data import DeviceMicrophoneVADEvent, DeviceScreenCapturedEvent, PipelineOutputLLMEvent, \
    PipelineImgCapEvent, \
    QQMessageEvent, DeviceMicrophoneSwitchEvent, PipelineOutputTTSEvent, PipelineASREvent, \
    PipelineOCREvent, SecondEvent, ConfigFileModifiedEvent
from event.event_emitter import emitter
from event.registry import EventKeyRegistry
from manager.config_manager import get_config
from pipeline.asr.asr_async import ASRAsyncPipeline
from pipeline.asr.asr_sync import ASRSyncPipeline
from pipeline.db.milvus.milvus_async import MilvusAsyncPipeline
from pipeline.db.milvus.milvus_sync import MilvusSyncPipeline
from pipeline.imgcap.imgcap_async import ImgCapAsyncPipeline
from pipeline.imgcap.imgcap_sync import ImgCapSyncPipeline
from pipeline.llm.llm_async import LLMAsyncPipeline
from pipeline.llm.llm_sync import LLMSyncPipeline
from pipeline.ocr.ocr_async import OCRAsyncPipeline
from pipeline.ocr.ocr_sync import avg_confidence, stringify, OCRSyncPipeline
from pipeline.tts.tts_async import TTSAsyncPipeline
from pipeline.tts.tts_sync import TTSSyncPipeline
from pipeline.vidcap.vidcap_async import VidCapAsyncPipeline
from pipeline.vidcap.vidcap_sync import VidCapSyncPipeline
from pipeline.vla.showui.showui_async import ShowUIAsyncPipeline
from pipeline.vla.showui.showui_sync import ShowUISyncPipeline

_config = get_config()


class BaseBot(ZerolanLiveRobotContext):
    def __init__(self):
        super().__init__()

    def reload_pipeline(self):
        config = get_config()

        # ASR Pipeline
        if self.asr is not None:
            if isinstance(self.asr, ASRSyncPipeline):
                self.asr = ASRSyncPipeline(config.pipeline.asr)
            elif isinstance(self.asr, ASRAsyncPipeline):
                self.asr = ASRAsyncPipeline(config.pipeline.asr)
            else:
                logger.error(f"Unsupported pipeline type: {type(self.asr)}")
        else:
            logger.warning("Pipeline asr will not reload because it has not been established.")

        # Vector Database Pipeline
        if self.vec_db is not None:
            if isinstance(self.vec_db, MilvusSyncPipeline):
                self.vec_db = MilvusSyncPipeline(config.pipeline.vec_db.milvus)
            elif isinstance(self.vec_db, MilvusAsyncPipeline):
                self.vec_db = MilvusAsyncPipeline(config.pipeline.vec_db.milvus)
            else:
                logger.error(f"Unsupported pipeline type: {type(self.vec_db)}")
        else:
            logger.warning("Pipeline vec_db will not reload because it has not been established.")

        # Image Captioning Pipeline
        if self.img_cap is not None:
            if isinstance(self.img_cap, ImgCapSyncPipeline):
                self.img_cap = ImgCapSyncPipeline(config.pipeline.img_cap)
            elif isinstance(self.img_cap, ImgCapAsyncPipeline):
                self.img_cap = ImgCapAsyncPipeline(config.pipeline.img_cap)
            else:
                logger.error(f"Unsupported pipeline type: {type(self.img_cap)}")
        else:
            logger.warning("Pipeline img_cap will not reload because it has not been established.")

        # LLM Pipeline
        if self.llm is not None:
            if isinstance(self.llm, LLMSyncPipeline):
                self.llm = LLMSyncPipeline(config.pipeline.llm)
            elif isinstance(self.llm, LLMAsyncPipeline):
                self.llm = LLMAsyncPipeline(config.pipeline.llm)
            else:
                logger.error(f"Unsupported pipeline type: {type(self.llm)}")
        else:
            logger.warning("Pipeline llm will not reload because it has not been established.")

        # OCR Pipeline
        if self.ocr is not None:
            if isinstance(self.ocr, OCRSyncPipeline):
                self.ocr = OCRSyncPipeline(config.pipeline.ocr)
            elif isinstance(self.ocr, OCRAsyncPipeline):
                self.ocr = OCRAsyncPipeline(config.pipeline.ocr)
            else:
                logger.error(f"Unsupported pipeline type: {type(self.ocr)}")
        else:
            logger.warning("Pipeline ocr will not reload because it has not been established.")

        # TTS Pipeline
        if self.tts is not None:
            if isinstance(self.tts, TTSSyncPipeline):
                self.tts = TTSSyncPipeline(config.pipeline.tts)
            elif isinstance(self.tts, TTSAsyncPipeline):
                self.tts = TTSAsyncPipeline(config.pipeline.tts)
            else:
                logger.error(f"Unsupported pipeline type: {type(self.tts)}")
        else:
            logger.warning("Pipeline tts will not reload because it has not been established.")

        # Video Captioning Pipeline
        if self.vid_cap is not None:
            if isinstance(self.vid_cap, VidCapSyncPipeline):
                self.vid_cap = VidCapSyncPipeline(config.pipeline.vid_cap)
            elif isinstance(self.vid_cap, VidCapAsyncPipeline):
                self.vid_cap = VidCapAsyncPipeline(config.pipeline.vid_cap)
            else:
                logger.error(f"Unsupported pipeline type: {type(self.vid_cap)}")
        else:
            logger.warning("Pipeline vid_cap will not reload because it has not been established.")

        # Show UI Pipeline
        if self.showui is not None:
            if isinstance(self.showui, ShowUISyncPipeline):
                self.showui = ShowUISyncPipeline(config.pipeline.showui)
            elif isinstance(self.showui, ShowUIAsyncPipeline):
                self.showui = ShowUIAsyncPipeline(config.pipeline.showui)
            else:
                logger.error(f"Unsupported pipeline type: {type(self.showui)}")
        else:
            logger.warning("Pipeline showui will not reload because it has not been established.")

        logger.info("Reloaded pipelines.")

    def reload_device(self):
        config = get_config()

        # Microphone
        if self.mic is not None:
            if config.system.default_enable_microphone:
                self.mic.resume()
            else:
                self.mic.pause()
        else:
            logger.info("Microphone will not reload because there is no microphone found.")

    async def start(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(emitter.start())

    async def stop(self):
        await emitter.stop()


class ZerolanLiveRobot(ZerolanLiveRobotContext):
    def __init__(self):
        super().__init__()
        self.cur_lang = Language.ZH
        self.tts_prompt_manager.set_lang(self.cur_lang)
        self._timer_flag = True
        self.tts_thread_pool = ThreadPoolExecutor(max_workers=1)
        self.init()

    async def start(self):

        if self.model_manager is not None:
            self.model_manager.scan()

        threads = []
        if _config.system.default_enable_microphone:
            vad_thread = KillableThread(target=self.mic.start, daemon=True, name="VADThread")
            threads.append(vad_thread)

        speaker_thread = KillableThread(target=self.speaker.start, daemon=True, name="SpeakerThread")
        threads.append(speaker_thread)

        playground_thread = KillableThread(target=self.playground.start, daemon=True, name="PlaygroundThread")
        threads.append(playground_thread)

        res_server_thread = KillableThread(target=self.res_server.start, daemon=True, name="ResServerThread")
        threads.append(res_server_thread)

        obs_client_thread = KillableThread(target=self.obs.start, daemon=True, name="ObsClientThread")
        threads.append(obs_client_thread)

        if self.game_agent:
            game_agent_thread = KillableThread(target=self.game_agent.start, daemon=True, name="GameAgentThread")
            threads.append(game_agent_thread)

        for thread in threads:
            thread.start()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(emitter.start())
            if self.bilibili:
                tg.create_task(self.bilibili.start())
            if self.youtube:
                tg.create_task(self.youtube.start())
            if self.twitch:
                tg.create_task(self.twitch.start())
            if self.config_page:
                tg.create_task(self.config_page.start())
            elapsed = 0
            while self._timer_flag:
                await asyncio.sleep(1)
                emitter.emit(SecondEvent(elapsed=elapsed))
                elapsed += 1

        for thread in threads:
            thread.join()

    async def stop(self):
        self.tts_thread_pool.shutdown()
        emitter.stop()
        kill_all_threads()
        await stop_all_runnable()
        logger.info("Good Bye!")

    def init(self):
        @emitter.on(EventKeyRegistry.Playground.CONNECTED)
        def on_playground_connected(_):
            self.mic.pause()
            logger.info("Because ZerolanPlayground client connected, close the local microphone.")
            self.playground.load_live2d_model(
                bot_id=self.bot_id,
                bot_display_name=self.bot_name,
                model_dir=self.live2d_model
            )
            logger.info(f"Live 2D model loaded: {self.live2d_model}")

        @emitter.on(EventKeyRegistry.Playground.DISCONNECTED)
        def on_playground_disconnected(_):
            # self.vad.resume()
            # logger.info("Because ZerolanPlayground client disconnected, open the local microphone.")
            pass

        @emitter.on(EventKeyRegistry.Device.MICROPHONE_SWITCH)
        def on_open_microphone(event: DeviceMicrophoneSwitchEvent):
            if self.mic.is_recording:
                if event.switch:
                    logger.warning("The microphone has already resumed.")
                    return
                self.mic.pause()
            else:
                if not event.switch:
                    logger.warning("The microphone has already paused.")
                    return
                self.mic.resume()

        @emitter.on(EventKeyRegistry.Device.MICROPHONE_VAD)
        def on_service_vad_speech_chunk(event: DeviceMicrophoneVADEvent):
            logger.debug("`SpeechEvent` received.")
            speech, channels, sample_rate = event.speech, event.channels, event.sample_rate
            query = ASRStreamQuery(is_final=True, audio_data=speech, channels=channels, sample_rate=sample_rate,
                                   media_type=event.audio_type.value)

            for prediction in self.asr.stream_predict(query):
                logger.info(f"ASR: {prediction.transcript}")
                emitter.emit(PipelineASREvent(prediction=prediction))
                logger.debug("ASREvent emitted.")

        @emitter.on(EventKeyRegistry.Pipeline.ASR)
        def asr_handler(event: PipelineASREvent):
            logger.debug("`ASREvent` received.")
            prediction = event.prediction
            self.playground.add_history(role="user", text=prediction.transcript, username=self.master_name)
            if "打开浏览器" in prediction.transcript:
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
                self.game_agent.exec_instruction(prediction.transcript)
            elif "看见" in prediction.transcript:
                img, img_save_path = self.screen.safe_capture(k=0.99)
                if not self.check_img(img):
                    return
                emitter.emit(DeviceScreenCapturedEvent(img_path=img_save_path, is_camera=False))
            elif "点击" in prediction.transcript:
                # If there is no display, then can not use this feature
                if os.environ.get('DISPLAY', None) is None:
                    return
                img, img_save_path = self.screen.safe_capture(k=0.99)
                if not self.check_img(img):
                    return

                query = ShowUiQuery(query=prediction.transcript, env="web", img_path=img_save_path)
                prediction = self.showui.predict(query)
                logger.debug("ShowUI: " + prediction.model_dump_json())
                action = prediction.actions[0]
                if action.action == "CLICK":
                    import pyautogui
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
                self.emit_llm_prediction(f"{memory}\n\n请根据上文回答：{prediction.transcript} \n")
            elif "加载模型" in prediction.transcript:
                file_id = find_file(self.model_manager.get_files(), prediction.transcript)
                file_info = self.model_manager.get_file_by_id(file_id)
                self.playground.load_3d_model(file_info)
            elif "调整模型" in prediction.transcript:
                info = self.playground.get_gameobjects_info()
                if not info:
                    logger.warning("No gameobjects info")
                    return
                so = model_scale(info, prediction.transcript)
                self.playground.modify_game_object_scale(so)
            else:
                tool_called = self.custom_agent.run(prediction.transcript)
                if tool_called:
                    logger.debug("Tool called.")
            if self.playground.is_connected:
                self.playground.show_user_input_text(prediction.transcript)
            if self.obs:
                self.obs.subtitle(prediction.transcript, which="user")
            self.emit_llm_prediction(prediction.transcript)

        # @emitter.on(EventKeyRegistry.LiveStream.DANMAKU)
        # def on_danmaku(event: LiveStreamDanmakuEvent):
        #     text = f"你收到了一条弹幕，用户“{event.danmaku.username}”说：\n{event.danmaku.content}"
        #     self.emit_llm_prediction(text)

        @emitter.on(EventKeyRegistry.System.SECOND)
        async def on_second_danmaku_check(event: SecondEvent):
            # Try select danmaku every 5 seconds.
            if event.elapsed % 5 == 0:
                danmaku = await self.bilibili.select_max_long_one()
                if danmaku:
                    logger.info(f"Selected danmaku: [{danmaku.username}] {danmaku.content}")
                    text = f"你收到了一条弹幕，用户“{danmaku.username}”说：\n{danmaku.content}"
                    self.emit_llm_prediction(text)

        @emitter.on(EventKeyRegistry.Device.SCREEN_CAPTURED)
        def on_device_screen_captured(event: DeviceScreenCapturedEvent):
            img_path = event.img_path
            if isinstance(event.img_path, Path):
                img_path = str(event.img_path)

            ocr_prediction = self.ocr.predict(OCRQuery(img_path=img_path))
            # TODO: 0.6 is a hyperparameter that indicates the average confidence of the text contained in the image.
            if avg_confidence(ocr_prediction) > 0.6:
                logger.info("OCR: " + stringify(ocr_prediction.region_results))
                emitter.emit(PipelineOCREvent(prediction=ocr_prediction))
            else:
                img_cap_prediction = self.img_cap.predict(ImgCapQuery(prompt="There", img_path=img_path))
                src_lang = Language.value_of(img_cap_prediction.lang)
                caption = translate(src_lang, self.cur_lang, img_cap_prediction.caption)
                img_cap_prediction.caption = caption
                logger.info("ImgCap: " + caption)
                emitter.emit(PipelineImgCapEvent(prediction=img_cap_prediction))

        @emitter.on(EventKeyRegistry.QQBot.QQ_MESSAGE)
        async def on_qq_message(event: QQMessageEvent):
            prediction = self.emit_llm_prediction(event.message, direct_return=True)
            if prediction is None:
                logger.warning("No response from LLM remote service and will not send QQ message.")
                return
            await self.qq.send_plain_message(prediction.response, event.group_id)

        @emitter.on(EventKeyRegistry.Pipeline.OCR)
        def on_pipeline_ocr(event: PipelineOCREvent):
            prediction = event.prediction
            text = "你看见了" + stringify(prediction.region_results) + "\n请总结一下"
            self.emit_llm_prediction(text)

        @emitter.on(EventKeyRegistry.Pipeline.IMG_CAP)
        def on_pipeline_img_cap(event: PipelineImgCapEvent):
            prediction = event.prediction
            text = "你看见了" + prediction.caption
            self.emit_llm_prediction(text)

        @emitter.on(EventKeyRegistry.Pipeline.LLM)
        def llm_query_handler(event: PipelineOutputLLMEvent):
            prediction = event.prediction
            text = prediction.response
            logger.info("LLM: " + text)
            sentiment = sentiment_analyse(sentiments=self.tts_prompt_manager.sentiments, text=text)
            tts_prompt = self.tts_prompt_manager.get_tts_prompt(sentiment)
            self.playground.add_history(role="assistant", text=text, username=self.bot_name)
            transcripts = split_by_punc(text, self.cur_lang)
            # Note that transcripts may be [] because we can not apply split in some cases.
            if len(transcripts) > 0:
                for idx, transcript in enumerate(transcripts):
                    self._tts_without_block(tts_prompt, transcript)
            else:
                self._tts_without_block(tts_prompt, text)

        @emitter.on(EventKeyRegistry.System.CONFIG_FILE_MODIFIED)
        def on_config_modified(_: ConfigFileModifiedEvent):
            config = get_config()

    def _tts_without_block(self, tts_prompt: TTSPrompt, text: str):
        def wrapper():
            query = TTSQuery(
                text=text,
                text_language="auto",
                refer_wav_path=tts_prompt.audio_path,
                prompt_text=tts_prompt.prompt_text,
                prompt_language=tts_prompt.lang,
                audio_type="wav"
            )
            prediction = self.tts.predict(query=query)
            logger.info(f"TTS: {query.text}")
            sample_rate, num_channels, duration = audio_util.get_audio_info(prediction.wave_data, prediction.audio_type)

            self.obs.subtitle(text, which="assistant", duration=math_util.clamp(0, 5, duration - 1))
            self.play_tts(PipelineOutputTTSEvent(prediction=prediction, transcript=text))

        # To sync audio playing and subtitle
        self.tts_thread_pool.submit(wrapper)

    def emit_llm_prediction(self, text, direct_return: bool = False) -> None | LLMPrediction:
        logger.debug("`emit_llm_prediction` called")
        query = LLMQuery(text=text, history=self.llm_prompt_manager.current_history)
        prediction = self.llm.predict(query)

        # Filter applied here
        is_filtered = self.filter.filter(prediction.response)
        if is_filtered:
            return

        # Remove \n start
        if prediction.response[0] == '\n':
            prediction.response = prediction.response[1:]

        logger.info(f"Length of current history: {len(self.llm_prompt_manager.current_history)}")
        self.llm_prompt_manager.reset_history(prediction.history, self.save_memory)
        if not direct_return:
            emitter.emit(PipelineOutputLLMEvent(prediction=prediction))
            logger.debug("LLMEvent emitted.")
        return prediction

    def change_lang(self, lang: Language):
        self.cur_lang = lang.name()
        self.tts_prompt_manager.set_lang(self.cur_lang)

    def check_img(self, img) -> bool:
        if is_image_uniform(img):
            logger.warning("Are you sure you capture the screen properly? The screen is black!")
            self.emit_llm_prediction("你忽然什么都看不见了！请向你的开发者求助！")
            return False
        return True

    def save_memory(self):
        start = len(self.llm_prompt_manager.injected_history)
        history = self.llm_prompt_manager.current_history[start:]
        ai_msg = summary_history(history)
        row = InsertRow(id=1, text=ai_msg.content, subject="history")
        insert = MilvusInsert(collection_name="history_collection", texts=[row])
        try:
            insert_res = self.vec_db.insert(insert)
            if insert_res.insert_count == 1:
                logger.info(f"Add a history memory: {row.text}")
            else:
                logger.warning(f"Failed to add a history memory.")
        except Exception as e:
            logger.warning("Milvus pipeline failed!")

    def play_tts(self, event: PipelineOutputTTSEvent):
        prediction = event.prediction
        audio_path = save_audio(wave_data=prediction.wave_data, format=AudioFileType(prediction.audio_type),
                                prefix='tts')
        if self.playground.is_connected:
            self.playground.play_speech(bot_id=self.bot_id, audio_path=audio_path,
                                        transcript=event.transcript, bot_name=self.bot_name)
            logger.debug("Remote speaker enqueue speech data")
        else:
            self.speaker.playsound(audio_path, block=True)
            logger.debug("Local speaker enqueue speech data")
