from loguru import logger

from framework.context import ZerolanLiveRobotContext
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
from pipeline.ocr.ocr_sync import OCRSyncPipeline
from pipeline.tts.tts_async import TTSAsyncPipeline
from pipeline.tts.tts_sync import TTSSyncPipeline
from pipeline.vidcap.vidcap_async import VidCapAsyncPipeline
from pipeline.vidcap.vidcap_sync import VidCapSyncPipeline
from pipeline.vla.showui.showui_async import ShowUIAsyncPipeline
from pipeline.vla.showui.showui_sync import ShowUISyncPipeline


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
