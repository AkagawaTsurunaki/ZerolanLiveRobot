from typing import Generator

from typeguard import typechecked
from zerolan.data.pipeline.llm import LLMQuery, LLMPrediction

from pipeline.base.base_async import BaseAsyncPipeline, get_base_url
from pipeline.defense.config import DefenseModelPipelineConfig, DefenseModelIdEnum


class DefenseLLMAsyncPipeline(BaseAsyncPipeline):
    def __init__(self, config: DefenseModelPipelineConfig):
        super().__init__(base_url=get_base_url(config.predict_url))
        self._model_id: DefenseModelIdEnum = config.model_id
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
