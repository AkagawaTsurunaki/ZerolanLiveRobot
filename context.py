import os

from agent.custom_agent import CustomAgent
from agent.tool_agent import ToolAgent
from event.speech_emitter import SpeechEmitter
from manager.config_manager import get_config
from manager.llm_prompt_manager import LLMPromptManager
from manager.model_manager import ModelManager
from manager.tts_prompt_manager import TTSPromptManager
from services.browser.browser import Browser
from devices.microphone import Microphone
from devices.speaker import Speaker
from character.filter.strategy import FirstMatchedFilter
from services.game.config import PlatformEnum
from services.game.minecraft.app import KonekoMinecraftAIAgent
from services.live_stream.service import LiveStreamService
from services.playground.bridge import PlaygroundBridge
from services.qqbot.bridge import QQBotBridge
from services.playground.res.res_server import ResourceServer
from pipeline.asr.asr_sync import ASRPipeline
from pipeline.synch.database import MilvusPipeline
from pipeline.synch.img_cap import ImgCapPipeline
from pipeline.llm.llm_sync import LLMSyncPipeline
from pipeline.synch.ocr import OCRPipeline
from pipeline.synch.tts import TTSPipeline
from pipeline.synch.vid_cap import VidCapPipeline
from pipeline.synch.vla import ShowUIPipeline

_config = get_config()


class ZerolanLiveRobotContext:
    """
    ZerolanLiveRobotContext 应只包括初始化上下文资源的工作，
    事件监听器注册和各类事件的发送逻辑不应该体现在这里。
    ZerolanLiveRobotContext here should only include initializing the context resource,
    The logic for registering listeners and sending events shouldn't be reflected here.
    """

    def __init__(self):
        self.llm: LLMSyncPipeline | None = None
        self.asr: ASRPipeline | None = None
        self.ocr: OCRPipeline | None = None
        self.tts: TTSPipeline | None = None
        self.img_cap: ImgCapPipeline | None = None
        self.vid_cap: VidCapPipeline | None = None
        self.showui: ShowUIPipeline | None = None
        self.vec_db: MilvusPipeline | None = None

        self.filter: FirstMatchedFilter | None = None
        self.llm_prompt_manager: LLMPromptManager | None = None
        self.tts_prompt_manager: TTSPromptManager | None = None
        self.live_stream: LiveStreamService | None = None

        self.tool_agent: ToolAgent | None = None
        self.microphone: Microphone | None = None

        if os.environ.get("DISPLAY", None) is not None:
            from devices.screen import Screen
            self.screen: Screen | None = Screen()
        else:
            self.screen = None

        self.browser: Browser | None = None
        self.speaker: Speaker | None = None
        self.playground: PlaygroundBridge | None = None
        self.qq: QQBotBridge | None = None

        self.bot_id: str | None = None
        self.bot_name: str | None = None
        self.master_name: str = "AkagawaTsurunaki"
        self.live2d_model: str | None = None
        self.res_server: ResourceServer | None = None

        assert _config.pipeline.llm.enable, f"At least LLMPipeline must be enabled in your config."
        self.llm = LLMSyncPipeline(_config.pipeline.llm)
        self.filter = FirstMatchedFilter(_config.character.chat.filter.bad_words)
        self.llm_prompt_manager = LLMPromptManager(_config.character.chat)
        self.speaker = Speaker()
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
            if _config.service.game.platform == PlatformEnum.minecraft:
                if self.tool_agent is None:
                    self.tool_agent = ToolAgent(_config.pipeline.llm)
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
