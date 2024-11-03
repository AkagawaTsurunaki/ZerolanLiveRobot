from dataclasses import dataclass


@dataclass
class ModelInfo:
    id: str
    path: str
    site: str
    langs: list[str] = None
    info: str = None


class ICModels:
    """
    图像字幕（Image Caption）模型
    """
    BLIP_IMG_CAP_LARGE = ModelInfo(
        id="Salesforce/blip-image-captioning-large",
        path="Salesforce/blip-image-captioning-large",
        site="https://huggingface.co/Salesforce/blip-image-captioning-large",
        info="只支持英文。",
        langs=["en"]
    )


class TTSModels:
    """
    语音转文字（Text to Speech）模型
    """
    GPT_SOVITS = ModelInfo(
        id="RVC-Boss/GPT-SoVITS",
        path="RVC-Boss/GPT-SoVITS",
        site="https://github.com/RVC-Boss/GPT-SoVITS",
        info="为了适配本项目，您需要下载 https://github.com/AkagawaTsurunaki/GPT-SoVITS 这个版本。",
        langs=["zh", "en", "ja"]
    )


class OCRModels:
    """
    光学字符识别（Optical Character Recognition）模型
    """
    PADDLE_OCR = ModelInfo(
        id="paddlepaddle/PaddleOCR",
        path="paddlepaddle/PaddleOCR",
        site="https://gitee.com/paddlepaddle/PaddleOCR",
        info="可能与环境冲突，请详见 PaddlePaddle 的官方文档。",
        langs=["zh", "en"]
    )


class VidCapModels:
    HITEA_BASE = ModelInfo(
        id="damo/multi-modal_hitea_video-captioning_base_en",
        path="damo/multi-modal_hitea_video-captioning_base_en",
        site="https://www.modelscope.cn/models/iic/multi-modal_hitea_video-captioning_base_en",
        info="需要额外安装魔搭环境",
        langs=["en"]
    )


class TTSModels:
    GPT_SOVITS = ModelInfo(
        id="AkagawaTsurunaki/GPT-SoVITS",
        path="AkagawaTsurunaki/GPT-SoVITS",
        site="https://github.com/AkagawaTsurunaki/GPT-SoVITS",
        info="需要按照该项目 README.md 文档进行安装",
        langs=["zh", "en", "ja"]
    )
