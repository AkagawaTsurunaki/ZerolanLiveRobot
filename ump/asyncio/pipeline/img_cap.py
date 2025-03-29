from typing import Literal

from typeguard import typechecked
from zerolan.data.pipeline.img_cap import ImgCapQuery, ImgCapPrediction

from ump.asyncio.pipeline.base import BaseAsyncPipeline, _parse_imgcap_query

ModelID = Literal['Salesforce/blip-image-captioning-large']


class ImgCapPipeline(BaseAsyncPipeline):
    def __init__(self, model_id: ModelID, base_url: str):
        super().__init__(base_url)
        self._model_id: ModelID = model_id
        self._predict_endpoint = "/img-cap/predict"
        self._stream_predict_endpoint = "/img-cap/stream-predict"

    @typechecked
    async def predict(self, query: ImgCapQuery) -> ImgCapPrediction:
        data = _parse_imgcap_query(query)
        async with self.session.post(self._predict_endpoint, data=data) as resp:
            return await resp.json(encoding='utf8', loads=ImgCapPrediction.model_validate_json)
