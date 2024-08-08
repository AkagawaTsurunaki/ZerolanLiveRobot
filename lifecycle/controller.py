import copy
import threading
from typing import List, Coroutine, Any

from loguru import logger

from common.buffer.danmaku_buffer import DanmakuBufferObject
from common.buffer.game_buf import MinecraftGameEvent
from common.config.chara_config import CustomCharacterConfig, TTSPrompt
from common.decorator import log_run_time
from common.enum.lang import Language
from common.utils import file_util
from lifecycle.env_data import MinecraftLiveStreamData
from manager.device.speaker import Speaker
from services.game.minecraft.app import MinecraftEventListeningApplication
from services.img_cap.pipeline import ImaCapPipeline
from services.live_stream.bilibili.service import BilibiliService
from services.llm.pipeline import LLMPipeline, LLMQuery, Conversation
from services.tts.pipeline import TTSPipeline, TTSQuery
from common.config.service_config import ServiceConfig as config
from common.utils.str_util import is_blank, split_by_punctuations, adjust_strings
from tasks.scnshoot_cap_task import ScreenshotCaptionTask
from tasks.sentiment_tts_prompt_task import SentimentTtsPromptTask


class Controller:
    def __init__(self):
        logger.info("初始化控制器中...")
        # 加载角色配置
        self._chara_config = CustomCharacterConfig()
        self._chara_config.load_config()
        self._history = [
                            Conversation(role="system", content=self._chara_config.system_prompt),
                        ] + copy.deepcopy(self._chara_config.example_cases)

        # Services and Pipelines
        self._llm_pipeline = LLMPipeline()
        self._tts_pipeline = TTSPipeline()
        self._bilibli_service = BilibiliService()
        self._game_service = MinecraftEventListeningApplication()
        self._imgcap_pipeline = ImaCapPipeline()

        # Tasks
        self._scnshot_cap_task = ScreenshotCaptionTask(self._llm_pipeline, self._imgcap_pipeline)
        self.sentiment_tts_prompt_task = SentimentTtsPromptTask(self._llm_pipeline, self._chara_config.tts_prompts)

        # Threads
        self.threads: List[threading.Thread] = []

        self._is_stream = False

    def awake(self):
        if config.live_stream_config.enable:
            self.threads.append(threading.Thread(target=self._bilibli_service.start))
        if config.game_config.enable:
            self.threads.append(threading.Thread(target=self._game_service.start))

        for thread in self.threads:
            thread.start()

    @log_run_time(lambda time_used: f"收集环境信息用时 {time_used} 秒")
    async def collect_env_input(self) -> MinecraftLiveStreamData | None:
        # 获取直播间弹幕
        dbo: DanmakuBufferObject | None = None
        if config.live_stream_config.enable:
            dbo = self._bilibli_service.danmaku_buf.select_latest_longest(k=4)

        # 获取游戏画面描述（异步）
        scnshot_cap_task = self._scnshot_cap_task.run(win_title='Minecraft', k=0.8)

        # 获取游戏事件
        mge: MinecraftGameEvent | None = None
        if config.game_config.enable:
            mge = self._game_service.game_evt_buf.select_last_one_and_clear()

        game_scn = await scnshot_cap_task

        result = MinecraftLiveStreamData(dev_say="",
                                         danmaku=dbo.danmaku if dbo is not None else None,
                                         game_scn=game_scn if not is_blank(game_scn) else None,
                                         game_env_info=mge if mge is not None else None)
        if not result.is_empty():
            logger.debug("环境数据采集完毕")
            return result
        else:
            logger.warning("无环境信息采集")
            return None

    async def update(self):
        env = await self.collect_env_input()
        if not env:
            return

        llm_query = LLMQuery(text=str(env), history=self._history)

        if self._is_stream:
            # 流式推理
            # 当你的 GPU 运算速率有限，或者瓶颈在 LLM 推理时请开启流式推理
            pass
        else:
            # 非流式推理
            # 非流式推理当您的 GPU 运算速率够快，可以忽略 LLM 推理时的延时时可以尝试启用
            llm_prediction = self._llm_pipeline.predict(llm_query)
            self._history = llm_prediction.history
            logger.info(f"角色说：{llm_prediction.response}")

            # 带情感的语音合成和播放
            tts_prompt = await self.sentiment_tts_prompt_task.run(llm_prediction.response)

            sentences = split_by_punctuations(llm_prediction.response)
            sentences = adjust_strings(sentences, 15)
            tts_tasks: List[Coroutine[Any, Any, str]] = []
            for sentence in sentences:
                tts_tasks.append(self.tts(sentence, tts_prompt))

            for tts_task in tts_tasks:
                tmp_wav_file = await tts_task
                Speaker.playsound(tmp_wav_file, block=True)

    async def tts(self, sentence: str, tts_prompt: TTSPrompt):
        tts_query = TTSQuery(text=sentence,
                             text_language=Language.ZH.name(),
                             refer_wav_path=tts_prompt.audio_path,
                             prompt_text=tts_prompt.transcript,
                             prompt_language=tts_prompt.lang.name())
        tts_prediction = self._tts_pipeline.predict(query=tts_query)
        tmp_wav_file = file_util.create_temp_file(prefix="tts", suffix=".wav", tmpdir="audio")
        with open(tmp_wav_file, "wb") as f:
            f.write(tts_prediction.wave_data)

        return tmp_wav_file
