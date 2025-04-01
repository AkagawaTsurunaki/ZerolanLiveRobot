import asyncio
import os

from loguru import logger

from agent.custom_agent import CustomAgent
from agent.tool_agent import ToolAgent
from common.config import get_config
from common.killable_thread import KillableThread
from common.utils.audio_util import save_tmp_audio
from event.event_data import TTSEvent
from event.event_emitter import emitter
from event.speech_emitter import SpeechEmitter
from manager.llm_prompt_manager import LLMPromptManager
from manager.model_manager import ModelManager
from manager.temp_data_manager import TempDataManager
from manager.tts_prompt_manager import TTSPromptManager
from services.browser.browser import Browser
from services.device.microphone import Microphone
from services.device.speaker import Speaker
from services.filter.strategy import FirstMatchedFilter
from services.game.minecraft.app import KonekoMinecraftAIAgent
from services.live_stream.service import LiveStreamService
from services.playground.bridge import PlaygroundBridge
from services.qqbot.bridge import QQBotBridge
from services.res_server import ResourceServer
from ump.pipeline.asr import ASRPipeline
from ump.pipeline.database import MilvusPipeline
from ump.pipeline.img_cap import ImgCapPipeline
from ump.pipeline.llm import LLMPipeline
from ump.pipeline.ocr import OCRPipeline
from ump.pipeline.tts import TTSPipeline
from ump.pipeline.vid_cap import VidCapPipeline
from ump.pipeline.vla import ShowUIPipeline

_config = get_config()


class ZerolanLiveRobotContext:
    """
    ZerolanLiveRobotContext 应只包括初始化上下文资源的工作，
    事件监听器注册和各类事件的发送逻辑不应该体现在这里。
    ZerolanLiveRobotContext here should only include initializing the context resource,
    The logic for registering listeners and sending events shouldn't be reflected here.
    """

    def __init__(self):
        self.llm: LLMPipeline | None = None
        self.asr: ASRPipeline | None = None
        self.ocr: OCRPipeline | None = None
        self.tts: TTSPipeline | None = None
        self.img_cap: ImgCapPipeline | None = None
        self.vid_cap: VidCapPipeline | None = None
        self.showui: ShowUIPipeline | None = None
        self.vec_db: MilvusPipeline | None = None

        self.filter: FirstMatchedFilter | None = None
        self.llm_prompt_manager: LLMPromptManager = None
        self.tts_prompt_manager: TTSPromptManager | None = None
        self.live_stream: LiveStreamService | None = None

        self.tool_agent: ToolAgent = None
        self.microphone: Microphone | None = None

        if os.environ.get("DISPLAY", None) is not None:
            from services.device.screen import Screen
            self.screen: Screen | None = Screen()
        else:
            self.screen = None

        self.browser: Browser | None = None
        self.speaker: Speaker = None
        self.playground: PlaygroundBridge = None
        self.qq: QQBotBridge = None

        self.bot_id: str = None
        self.bot_name: str = None
        self.master_name: str = "AkagawaTsurunaki"
        self.live2d_model: str = None
        self.res_server: ResourceServer | None = None

        self.temp_data_manager: TempDataManager = TempDataManager()

        assert _config.pipeline.llm.enable, f"At least LLMPipeline must be enabled in your config."
        self.llm = LLMPipeline(_config.pipeline.llm)
        self.filter = FirstMatchedFilter(_config.character.chat.filter.bad_words)
        self.llm_prompt_manager = LLMPromptManager(_config.character.chat)
        self.speaker = Speaker()
        self.temp_data_manager.create_temp_dir()
        self.bot_name = _config.character.bot_name
        self.res_server = ResourceServer(_config.service.res_server.host, _config.service.res_server.port)

        if _config.pipeline.asr.enable:
            self.asr = ASRPipeline(_config.pipeline.asr)
        if _config.pipeline.ocr.enable:
            self.ocr = OCRPipeline(_config.pipeline.ocr)
        if _config.pipeline.tts.enable:
            self.tts_prompt_manager = TTSPromptManager(_config.character.speech)
            self.tts = TTSPipeline(_config.pipeline.tts)
        if _config.pipeline.img_cap.enable:
            self.img_cap = ImgCapPipeline(_config.pipeline.img_cap)
        if _config.pipeline.vid_cap.enable:
            self.vid_cap = VidCapPipeline(_config.pipeline.vid_cap)
        if _config.pipeline.vla.enable:
            if _config.pipeline.vla.showui.enable:
                self.showui = ShowUIPipeline(_config.pipeline.vla.showui)
        if _config.service.browser.enable:
            self.browser = Browser(_config.external_tool.browser)
        if _config.service.game.enable:
            if _config.service.game.platform == "minecraft":
                self.game_agent = KonekoMinecraftAIAgent(_config.service.game, self.tool_agent)
        if _config.service.live_stream.enable:
            self.live_stream = LiveStreamService(_config.service.live_stream)
        if _config.pipeline.vec_db.enable:
            self.vec_db = MilvusPipeline(_config.pipeline.vec_db.milvus)
        if _config.service.playground.enable:
            self.model_manager = ModelManager()
            self.bot_id = _config.service.playground.bot_id
            self.live2d_model = _config.service.playground.model_dir
            self.custom_agent = CustomAgent(config=_config.pipeline.llm)
            self.playground = PlaygroundBridge(config=_config.service.playground)
        if _config.service.qqbot.enable:
            self.qq = QQBotBridge(_config.service.qqbot)
        self.microphone = Microphone()
        self.vad = SpeechEmitter(self.microphone)

        # Agents
        self.tool_agent = ToolAgent(_config.pipeline.llm)

    async def start(self):

        if self.model_manager is not None:
            self.model_manager.scan()

        threads = []
        if _config.system.default_enable_microphone:
            vad_thread = KillableThread(target=self.vad.start, daemon=True, name="VADThread")
            threads.append(vad_thread)

        speaker_thread = KillableThread(target=self.speaker.start, daemon=True, name="SpeakerThread")
        threads.append(speaker_thread)

        playground_thread = KillableThread(target=self.playground.start, daemon=True, name="PlaygroundThread")
        threads.append(playground_thread)

        res_server_thread = KillableThread(target=self.res_server.start, daemon=True, name="ResServerThread")
        threads.append(res_server_thread)

        for thread in threads:
            thread.start()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(emitter.start())
            if self.live_stream is not None:
                tg.create_task(self.live_stream.start())

        for thread in threads:
            thread.join()

    def play_tts(self, event: TTSEvent):
        prediction = event.prediction
        if self.playground.is_connected:
            audio_path = save_tmp_audio(prediction.wave_data)
            self.playground.play_speech(bot_id=self.bot_id, audio_path=audio_path,
                                        transcript=event.transcript, bot_name=self.bot_name)
            logger.debug("Remote speaker enqueue speech data")
        else:
            self.speaker.enqueue_sound(prediction.wave_data)
            logger.debug("Local speaker enqueue speech data")
