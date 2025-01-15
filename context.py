from agent.custom_agent import CustomAgent
from agent.tool_agent import ToolAgent
from common.config import get_config
from manager.llm_prompt_manager import LLMPromptManager
from manager.model_manager import ModelManager
from manager.temp_data_manager import TempDataManager
from manager.tts_prompt_manager import TTSPromptManager
from zerolan.ump.pipeline.asr import ASRPipeline
from zerolan.ump.pipeline.database import MilvusPipeline
from zerolan.ump.pipeline.img_cap import ImgCapPipeline
from zerolan.ump.pipeline.llm import LLMPipeline
from zerolan.ump.pipeline.ocr import OCRPipeline
from zerolan.ump.pipeline.tts import TTSPipeline
from zerolan.ump.pipeline.vid_cap import VidCapPipeline
from zerolan.ump.pipeline.vla import ShowUIPipeline
from services.browser.browser import Browser
from services.device.screen import Screen
from services.device.speaker import Speaker
from services.filter.strategy import FirstMatchedFilter
from services.game.minecraft.app import KonekoMinecraftAIAgent
from services.live2d.app import Live2dApplication
from services.live_stream.service import LiveStreamService
from services.viewer.app import ZerolanViewerServer

config = get_config()


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
        self.screen: Screen | None = None
        self.browser: Browser | None = None
        self.speaker: Speaker = None
        self.live2d: Live2dApplication | None = None
        self.viewer: ZerolanViewerServer | None = None

        self.temp_data_manager: TempDataManager = TempDataManager()
        self._init()

    def _init(self):
        assert config.pipeline.llm.enable, f"At least LLMPipeline must be enabled in your config."
        self.llm = LLMPipeline(config.pipeline.llm)
        self.filter = FirstMatchedFilter(config.character.chat.filter.bad_words)
        self.llm_prompt_manager = LLMPromptManager(config.character.chat)
        self.speaker = Speaker()
        self.temp_data_manager.create_temp_dir()

        if config.pipeline.asr.enable:
            self.asr = ASRPipeline(config.pipeline.asr)
        if config.pipeline.ocr.enable:
            self.ocr = OCRPipeline(config.pipeline.ocr)
            self.screen = Screen()
        if config.pipeline.tts.enable:
            self.tts_prompt_manager = TTSPromptManager(config.character.speech)
            self.tts = TTSPipeline(config.pipeline.tts)
        if config.pipeline.img_cap.enable:
            self.img_cap = ImgCapPipeline(config.pipeline.img_cap)
            self.screen = Screen()
        if config.pipeline.vid_cap.enable:
            self.vid_cap = VidCapPipeline(config.pipeline.vid_cap)
        if config.pipeline.vla.enable:
            if config.pipeline.vla.showui.enable:
                self.showui = ShowUIPipeline(config.pipeline.vla.showui)
        if config.external_tool.browser.enable:
            self.browser = Browser(config.external_tool.browser)
        if config.service.game.enable:
            if config.service.game.platform == "minecraft":
                self.game_agent = KonekoMinecraftAIAgent(config.service.game, self.tool_agent)
        if config.service.live_stream.enable:
            self.live_stream = LiveStreamService(config.service.live_stream)
        if config.service.live2d.enable:
            self.live2d = Live2dApplication(config.service.live2d)
        if config.pipeline.vec_db.enable:
            self.vec_db = MilvusPipeline(config.pipeline.vec_db.milvus)
        if config.service.viewer.enable:
            self.viewer = ZerolanViewerServer(host=config.service.viewer.host, port=config.service.viewer.port,
                                              protocol="ZerolanViewerProtocol", version="1.0")
            self.model_manager = ModelManager()
            self.custom_agent = CustomAgent(config=config.pipeline.llm, viewer=self.viewer)

        # Agents
        self.tool_agent = ToolAgent(config.pipeline.llm)
