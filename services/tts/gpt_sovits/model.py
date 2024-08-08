from typing import Any
from loguru import logger
from common.abs_model import AbstractModel
from common.register.model_register import TTSModels


class GPT_SoVITS(AbstractModel):
    def __init__(self):
        super().__init__()
        self.model_id = TTSModels.GPT_SOVITS.id

    def load_model(self):
        logger.warning(TTSModels.GPT_SOVITS.info)

    def predict(self, *args, **kwargs) -> Any:
        raise NotImplementedError("不应该直接调用本方法")

    def stream_predict(self, *args, **kwargs) -> Any:
        raise NotImplementedError("不应该直接调用本方法")
