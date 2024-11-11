import asyncio
import copy
import threading
from typing import List, Coroutine, Any

from loguru import logger
from zerolan.ui.api.toasts import Toast

from pipeline.llm import LLMPipeline
from zerolan_live_robot_core.abs_app import AppStatusEnum
from common.buffer.danmaku_buffer import DanmakuBufferObject
from common.buffer.game_buf import MinecraftGameEvent
from common.config.chara_config import CustomCharacterConfig, TTSPrompt
from common.decorator import log_run_time
from common.enum.lang import Language
from common.utils import file_util, audio_util
from lifecycle.env_data import CustomLiveStreamData
from services.device.speaker import Speaker
from services.filter.strategy import FirstMatchedFilter
from services.game.minecraft.app import KonekoMinecraftAIAgent
from pipeline.img_cap import ImaCapPipeline
from services.live_stream.bilibili.service import BilibiliService
from zerolan_live_robot_data.data.llm import LLMQuery, Conversation
from pipeline.pipeline import TTSPipeline, TTSQuery
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

        # Filter
        self._content_filter = FirstMatchedFilter()
        self._content_filter.set_words(self._chara_config.bad_words)

        # Services and Pipelines
        self._llm_pipeline = LLMPipeline()
        self._tts_pipeline = TTSPipeline()
        self._bilibli_service = BilibiliService()
        self._game_service = KonekoMinecraftAIAgent()
        self._imgcap_pipeline = ImaCapPipeline()

        # 这里去检验服务是否都已经启动
        self.check_service_state()

        # Tasks
        self._scnshot_cap_task = ScreenshotCaptionTask(self._llm_pipeline, self._imgcap_pipeline)
        self.sentiment_tts_prompt_task = SentimentTtsPromptTask(self._llm_pipeline, self._chara_config.tts_prompts)
        self._game_task = None

        # Threads
        self.threads: List[threading.Thread] = []

        self._is_stream = False

    def check_service_state(self):
        """
        检查服务是否正常运行。存在异常将会退出整个程序。
        """
        status = {"LLM": self._llm_pipeline.check_state(),
                  "TTS": self._tts_pipeline.check_state(),
                  "Image Captioning": self._imgcap_pipeline.check_state()}
        flag = False
        for service, state in status.items():
            if state.state != AppStatusEnum.RUNNING:
                logger.error(f"{service} 服务异常")
                flag = True

        if flag:
            msg = "部分关键服务存在异常，进程结束。"
            logger.error(msg)
            Toast(message=msg, level="error").show_toast()
            exit(0)

    async def awake(self):
        if config.live_stream_config.enable:
            self.threads.append(threading.Thread(target=self._bilibli_service.start))
        if config.game_config.enable:
            self._game_task = asyncio.create_task(self._game_service.start())

        for thread in self.threads:
            thread.start()

    @log_run_time(lambda time_used: f"收集环境信息用时 {time_used} 秒")
    async def collect_env_input(self) -> CustomLiveStreamData | None:
        # 获取直播间弹幕
        dbo: DanmakuBufferObject | None = None
        if config.live_stream_config.enable:
            dbo = self._bilibli_service.danmaku_buf.select_latest_longest(k=4)

        # 获取游戏画面描述（异步）
        scnshot_cap_task = self._scnshot_cap_task.run(win_title='Minecraft', k=0.8)

        # 获取游戏事件
        game_event: MinecraftGameEvent | None = None
        if config.game_config.enable:
            game_event = self._game_service.game_evt_buf.select_last_one_and_clear()
        game_scn = None

        # 将画面解释为自然语言
        try:
            game_scn = await scnshot_cap_task
        except Exception as e:
            logger.exception(e)
            Toast(message="🧠⇆❌️⇆👁️ 视觉系统故障", level="error").show_toast()

        result = CustomLiveStreamData(dev_say="",
                                      danmaku=dbo.danmaku if dbo is not None else None,
                                      game_scene=game_scn if not is_blank(game_scn) else None,
                                      game_event=game_event if game_event is not None else None)
        if result.is_meaningful():
            logger.debug("环境数据采集完毕")
            return result
        else:
            logger.warning("无环境信息采集")
            return None

    async def update(self):
        env = await self.collect_env_input()
        if not env:
            return

        llm_query = LLMQuery(text=env.interpret(), history=self._history)

        if self._is_stream:
            # 流式推理
            # 当你的 GPU 运算速率有限，或者瓶颈在 LLM 推理时请开启流式推理
            raise NotImplementedError("这一部分尚未实现")
        else:
            # 非流式推理
            # 非流式推理当您的 GPU 运算速率够快，可以忽略 LLM 推理时的延时时可以尝试启用
            try:
                llm_prediction = self._llm_pipeline.predict(llm_query)
            except Exception as e:
                logger.exception(e)
                Toast(message="🧠⇆❌️⇆💭 语言系统故障", level="error").show_toast()
                raise e
            self._history = llm_prediction.history
            logger.info(f"角色说：{llm_prediction.response}")

            ### TODO: Remember to test here
            if not self._content_filter.filter(llm_prediction.response):
                logger.warning("本次对话存在敏感内容，已被过滤")
                return
            ###

            # 带情感的语音合成和播放
            tts_prompt = await self.sentiment_tts_prompt_task.run(llm_prediction.response)

            sentences = split_by_punctuations(llm_prediction.response)
            sentences = adjust_strings(sentences, 15)
            tts_tasks: List[Coroutine[Any, Any, str]] = []
            for sentence in sentences:
                tts_tasks.append(self.tts(sentence, tts_prompt))

            for idx, tts_task in enumerate(tts_tasks):
                tmp_wav_file = await tts_task
                _, _, duration = audio_util.check_wav_info(tmp_wav_file)
                Toast(message=sentences[idx], duration=duration, level="info").show_toast()
                Speaker.playsound(tmp_wav_file, block=True)

    async def tts(self, sentence: str, tts_prompt: TTSPrompt):
        tts_query = TTSQuery(text=sentence,
                             text_language=Language.ZH.name(),
                             refer_wav_path=tts_prompt.audio_path,
                             prompt_text=tts_prompt.transcript,
                             prompt_language=tts_prompt.lang.name())
        try:
            tts_prediction = self._tts_pipeline.predict(query=tts_query)
        except Exception as e:
            logger.exception(e)
            Toast(message="🧠⇆❌️⇆🗣️ 语音系统故障", level="error").show_toast()
            raise e

        tmp_wav_file = file_util.create_temp_file(prefix="tts", suffix=".wav", tmpdir="audio")
        with open(tmp_wav_file, "wb") as f:
            f.write(tts_prediction.wave_data)

        return tmp_wav_file
