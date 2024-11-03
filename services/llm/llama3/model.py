from typing import Any

import transformers
import torch

from common.abs_model import AbstractModel
from common.decorator import log_model_loading
from common.register.model_register import LLMModels
from zerolan_live_robot_data.data.llm import LLMQuery

model_id = "meta-llama/Meta-Llama-3-70B"


class Llama3_70B(AbstractModel):

    def __init__(self):
        super().__init__()
        self._model = None

    @log_model_loading(LLMModels.LLAMA3_70B)
    def load_model(self):
        self._model = transformers.pipeline(
            "text-generation", model=model_id, model_kwargs={"torch_dtype": torch.bfloat16}, device_map="auto"
        )

    def predict(self, query: LLMQuery):
        self._model("Hey how are you doing today?")
        pass

    def stream_predict(self, query: LLMQuery) -> Any:
        pass
