from typing import Generator, Literal

from typeguard import typechecked
from zerolan.data.pipeline.llm import LLMQuery, LLMPrediction

from pipeline.asynch.base import BaseAsyncPipeline

ModelID = Literal[
    "THUDM/chatglm3-6b", "THUDM/GLM-4",
    "Qwen/Qwen-7B-Chat", "augmxnt/shisa-7b-v1", "01-ai/Yi-6B-Chat", "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"]


class LLMPipeline(BaseAsyncPipeline):
    def __init__(self, model_id: ModelID, base_url: str):
        super().__init__(base_url)
        self._model_id: ModelID = model_id
        self._base_url = base_url
        self._predict_endpoint = "/llm/predict"
        self._stream_predict_endpoint = "/llm/stream-predict"

    @typechecked
    async def predict(self, query: LLMQuery) -> LLMPrediction:
        async with self.session.post(self._predict_endpoint, json=query.model_dump()) as resp:
            return await resp.json(encoding='utf8', loads=LLMPrediction.model_validate_json)

    @typechecked
    async def stream_predict(self, query: LLMQuery) -> Generator[LLMPrediction, None, None]:
        async with self.session.post(self._stream_predict_endpoint, json=query.model_dump()) as resp:
            return await resp.json(encoding='utf8', loads=LLMPrediction.model_validate_json)
