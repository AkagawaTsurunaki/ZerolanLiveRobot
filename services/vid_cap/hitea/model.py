"""
mPLUG-HiTeA-视频描述-英文-Base
https://www.modelscope.cn/models/iic/multi-modal_hitea_video-captioning_base_en
"""
import os.path
from typing import Any

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

from common.abs_model import AbstractModel
from common.config.model_config import ModelConfigLoader
from common.decorator import log_model_loading
from common.register.model_register import VidCapModels
from services.vid_cap.pipeline import VidCapQuery, VidCapPrediction

config = ModelConfigLoader.hitea_base_model_config


# 可能遇到的问题
#   1. 安装 fairseq 需要使用 pip 版本 24.0
#       https://github.com/facebookresearch/fairseq/issues/5518
#   2. 运行出现 TypeError: VideoCaptioningPipeline: HiTeAForAllTasks: 'NoneType' object is not callable
#       https://github.com/modelscope/modelscope/issues/265
#       请安装 fairscale

class HiteaBaseModel(AbstractModel):
    def __init__(self):
        super().__init__()
        self._model = None
        self._lang = "en"
        self._model_path = config.model_path

    @log_model_loading(VidCapModels.HITEA_BASE)
    def load_model(self):
        self._model = pipeline(Tasks.video_captioning, model=self._model_path)
        assert self._model is not None, "模型加载失败"

    def predict(self, query: VidCapQuery) -> VidCapPrediction:
        assert os.path.exists(query.vid_path), f"视频路径不存在：{query.vid_path}"
        caption = self._model(query.vid_path)['caption']
        return VidCapPrediction(caption=caption, lang=self._lang)

    def stream_predict(self, *args, **kwargs) -> Any:
        raise NotImplementedError()
