from agent.tool_agent import ToolAgent
from common.config import get_config
from manager.llm_prompt_manager import LLMPromptManager
from manager.tts_prompt_manager import TTSPromptManager
from pipeline.asr import ASRPipeline
from pipeline.img_cap import ImgCapPipeline
from pipeline.llm import LLMPipeline
from pipeline.ocr import OCRPipeline
from pipeline.tts import TTSPipeline
from pipeline.vid_cap import VidCapPipeline
from services.device.screen import Screen
from services.filter.strategy import FirstMatchedFilter

config = get_config()


class ZerolanLiveRobotContext:

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
        self.init()

    def init(self):
        assert config.pipeline.llm.enable, f"At least LLMPipeline must be enabled in your config."
        self.llm = LLMPipeline(config.pipeline.llm)
        self.filter = FirstMatchedFilter(config.character.chat.filter.bad_words)
        self.llm_prompt_manager = LLMPromptManager(config.character.chat)
        self.tool_agent = ToolAgent(config.pipeline.llm)

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
