from loguru import logger
from zerolan.pipeline.asr.asr_sync import ASRPipeline
from zerolan.pipeline.db.milvus.milvus_sync import MilvusPipeline
from zerolan.pipeline.imgcap.imgcap_sync import ImgCapPipeline
from zerolan.pipeline.llm.llm_sync import LLMPipeline

from framework.context import ZerolanLiveRobotContext
from manager.config_manager import get_config
from zerolan.pipeline.ocr.ocr_sync import OCRPipeline
from zerolan.pipeline.tts.tts_sync import TTSPipeline
from zerolan.pipeline.vidcap.vidcap_sync import VidCapPipeline
from zerolan.pipeline.vla.showui.showui_sync import ShowUIPipeline


class BaseBot(ZerolanLiveRobotContext):
    def __init__(self):
        super().__init__()

    def reload_pipeline(self):
        config = get_config()

        # ASR Pipeline
        if self.asr is not None:
            self.asr = ASRPipeline(config.pipeline.asr)

        # Vector Database Pipeline
        if self.vec_db is not None:
            self.vec_db = MilvusPipeline(config.pipeline.vec_db.milvus)

        if self.img_cap is not None:
            self.img_cap = ImgCapPipeline(config.pipeline.img_cap)

        if self.llm is not None:
            self.llm = LLMPipeline(config.pipeline.llm)

        if self.ocr is not None:
            self.ocr = OCRPipeline(config.pipeline.ocr)

        if self.tts is not None:
            self.tts = TTSPipeline(config.pipeline.tts)

        if self.vid_cap is not None:
            self.vid_cap = VidCapPipeline(config.pipeline.vid_cap)

        # Show UI Pipeline
        if self.showui is not None:
            self.showui = ShowUIPipeline(config.pipeline.showui)
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
