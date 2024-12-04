from agent.location_attn import LocationAttentionAgent
from agent.sentiment import SentimentAnalyzerAgent
from agent.tool_agent import ToolAgent
from agent.translator import TranslatorAgent
from common.config import get_config
from manager.llm_prompt_manager import LLMPromptManager
from manager.tts_prompt_manager import TTSPromptManager
from pipeline.asr import ASRPipeline
from pipeline.img_cap import ImgCapPipeline
from pipeline.llm import LLMPipeline
from pipeline.ocr import OCRPipeline
from pipeline.tts import TTSPipeline
from pipeline.vid_cap import VidCapPipeline
from services.browser.browser import Browser
from services.device.screen import Screen
from services.device.speaker import Speaker
from services.filter.strategy import FirstMatchedFilter
from services.game.minecraft.app import KonekoMinecraftAIAgent
from services.live_stream.service import LiveStreamService

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

        self.filter: FirstMatchedFilter | None = None
        self.llm_prompt_manager: LLMPromptManager = None
        self.tts_prompt_manager: TTSPromptManager | None = None

        self.tool_agent: ToolAgent = None
        self.screen: Screen | None = None
        self.browser: Browser | None = None
        self.speaker: Speaker = None
        self._init()

    def _init(self):
        assert config.pipeline.llm.enable, f"At least LLMPipeline must be enabled in your config."
        self.llm = LLMPipeline(config.pipeline.llm)
        self.filter = FirstMatchedFilter(config.character.chat.filter.bad_words)
        self.llm_prompt_manager = LLMPromptManager(config.character.chat)
        self.speaker = Speaker()

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
        if config.external_tool.browser.enable:
            self.browser = Browser(config.external_tool.browser)
        if config.service.game.enable:
            if config.service.game.platform == "minecraft":
                self.game_agent = KonekoMinecraftAIAgent(config.service.game, self.tool_agent)
        if config.service.live_stream.enable:
            self.live_stream = LiveStreamService(config.service.live_stream)

        # Agents
        self.tool_agent = ToolAgent(config.pipeline.llm)
        self.translator_agent = TranslatorAgent(config.pipeline.llm)
        self.location_attention_agent = LocationAttentionAgent(config.pipeline.llm)
        if self.tts_prompt_manager is not None:
            self.sentiment_analyzer_agent = SentimentAnalyzerAgent(self.tts_prompt_manager, config.pipeline.llm)
