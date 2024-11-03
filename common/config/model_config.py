from dataclasses import dataclass, field
from typing import List, Literal

from common.register.model_register import ASRModels, ICModels, OCRModels, VidCapModels
from common.utils.file_util import spath


@dataclass
class BlipModelConfig:
    model_path: str = ICModels.BLIP_IMG_CAP_LARGE.path
    device: str = "cuda"


@dataclass
class PaddleOCRModelConfig:
    model_path: str = OCRModels.PADDLE_OCR.path
    lang: Literal["ch", "en", "fr", "german", "korean", "japan"] = "ch"


@dataclass
class HiteaBaseModelConfig:
    model_path: str = VidCapModels.HITEA_BASE.path
    task: Literal["video-captioning"] = "video-captioning"


class ModelConfigLoader:
    speech_paraformer_model_config: SpeechParaformerModelConfig | None = None
    blip_model_config: BlipModelConfig | None = None
    paddle_ocr_model_config: PaddleOCRModelConfig | None = None
    hitea_base_model_config: HiteaBaseModelConfig | None = None

    @staticmethod
    def load_config():
        import yaml
        with open(spath("resources/config/models_config.yaml"), 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

            asr_config_data = config_data.get("ASR", None)
            if asr_config_data is not None:
                ModelConfigLoader.speech_paraformer_model_config = SpeechParaformerModelConfig(
                    **asr_config_data.get('SpeechParaformerModelConfig', {}))

            imgcap_config_data = config_data.get("IC", None)
            if imgcap_config_data is not None:
                ModelConfigLoader.blip_model_config = BlipModelConfig(**imgcap_config_data.get('BlipModelConfig', {}))

            ocr_config_data = config_data.get("OCR", None)
            if ocr_config_data is not None:
                ModelConfigLoader.paddle_ocr_model_config = PaddleOCRModelConfig(
                    **ocr_config_data.get('PaddleOCRModelConfig', {}))

            vidcap_config_data = config_data.get("VidCap", None)
            if vidcap_config_data is not None:
                ModelConfigLoader.hitea_base_model_config = HiteaBaseModelConfig(
                    **vidcap_config_data.get('HiteaBaseModelConfig', {})
                )


ModelConfigLoader.load_config()
