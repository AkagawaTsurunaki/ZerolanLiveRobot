from typing import Literal

from typeguard import typechecked
from zerolan.data.pipeline.vla import ShowUiPrediction, ShowUiQuery

from ump.asyncio.pipeline.base import BaseAsyncPipeline

ModelID = Literal['showlab/ShowUI-2B']


class ShowUIPipeline(BaseAsyncPipeline):
    def __init__(self, model_id: ModelID, base_url: str):
        super().__init__(base_url)
        self._model_id: ModelID = model_id
        self._predict_endpoint = "/vla/showui/predict"

    @typechecked
    async def predict(self, query: ShowUiQuery) -> ShowUiPrediction:
        async with self.session.post(self._predict_endpoint, json=query.model_dump()) as resp:
            return await resp.json(encoding='utf8', loads=ShowUiPrediction.model_validate_json)
