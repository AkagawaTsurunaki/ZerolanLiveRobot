from typing import Any

import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

from common.abs_model import AbstractModel
from common.config.model_config import ModelConfigLoader
from common.decorator import log_model_loading
from common.register.model_register import ICModels
from services.img_cap.pipeline import ImgCapQuery, ImgCapPrediction

config = ModelConfigLoader.blip_model_config


class BlipImageCaptioningLarge(AbstractModel):

    def __init__(self):
        super().__init__()
        self.model_id = ICModels.BLIP_IMG_CAP_LARGE.id
        self._lang = ICModels.BLIP_IMG_CAP_LARGE.langs[0]
        self._model = None
        self._processor = None
        self._model_path = config.model_path
        self._device = config.device

    @log_model_loading(ICModels.BLIP_IMG_CAP_LARGE)
    def load_model(self):
        self._processor = BlipProcessor.from_pretrained(self._model_path)
        self._model = BlipForConditionalGeneration.from_pretrained(self._model_path, torch_dtype=torch.float16).to(
            self._device)

    def predict(self, query: ImgCapQuery) -> ImgCapPrediction:
        raw_image = Image.open(query.img_path)
        # 条件式图片转字幕
        inputs = self._processor(raw_image, query.prompt, return_tensors="pt").to(self._device, torch.float16)

        out = self._model.generate(**inputs)
        output_text = self._processor.decode(out[0], skip_special_tokens=True)

        return ImgCapPrediction(caption=output_text, lang="en")

    def stream_predict(self, *args, **kwargs) -> Any:
        raise NotImplementedError("未实现方法")
