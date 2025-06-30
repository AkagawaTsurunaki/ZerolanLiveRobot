from typing import Literal

from typeguard import typechecked
from zerolan.data.pipeline.img_cap import ImgCapQuery, ImgCapPrediction

from pipeline.base.base_async import BaseAsyncPipeline, _parse_imgcap_query, get_base_url
from pipeline.imgcap.config import ImgCapPipelineConfig, ImgCapModelIdEnum


class ImgCapAsyncPipeline(BaseAsyncPipeline):
    def __init__(self, config: ImgCapPipelineConfig):
        super().__init__(base_url=get_base_url(config.predict_url))
        self._model_id: ImgCapModelIdEnum = config.model_id
        self._predict_endpoint = "/img-cap/predict"
        self._stream_predict_endpoint = "/img-cap/stream-predict"

    @typechecked
    async def predict(self, query: ImgCapQuery) -> ImgCapPrediction:
        data = _parse_imgcap_query(query)
        async with self.session.post(self._predict_endpoint, data=data) as resp:
            return await resp.json(encoding='utf8', loads=ImgCapPrediction.model_validate_json)
