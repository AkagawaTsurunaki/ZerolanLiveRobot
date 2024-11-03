from dataclasses import dataclass, field
from typing import List, Literal

from common.register.model_register import ASRModels, ICModels, OCRModels, VidCapModels
from common.utils.file_util import spath


@dataclass
class SpeechParaformerModelConfig:
    """
    Speech Paraformer 的配置
    引用：
        https://modelscope.cn/models/iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1/summary
    """

    model_path: str = ASRModels.SPEECH_PARAFORMER_ASR.path
    chunk_size: List[int] = field(default_factory=lambda: [0, 10, 5])  # [0, 10, 5] 600ms, [0, 8, 4] 480ms
    encoder_chunk_look_back: int = 4  # number of chunks to lookback for encoder self-attention
    decoder_chunk_look_back: int = 1  # number of encoder chunks to lookback for decoder cross-attention
    version: str = "v2.0.4"
    chunk_stride: int = 10 * 960  # chunk_size[1] * 960


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
