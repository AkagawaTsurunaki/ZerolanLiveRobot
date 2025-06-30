from typing import Literal

from typeguard import typechecked
from zerolan.data.pipeline.ocr import OCRQuery, OCRPrediction

from pipeline.base.base_async import BaseAsyncPipeline, _parse_imgcap_query, get_base_url
from pipeline.ocr.config import OCRPipelineConfig, OCRModelIdEnum


class OCRAsyncPipeline(BaseAsyncPipeline):
    def __init__(self, config: OCRPipelineConfig):
        super().__init__(base_url=get_base_url(config.predict_url))
        self._model_id: OCRModelIdEnum = config.model_id
        self._predict_endpoint = "/ocr/predict"
        self._stream_predict_endpoint = "/ocr/stream-predict"

    @typechecked
    async def predict(self, query: OCRQuery) -> OCRPrediction:
        data = _parse_imgcap_query(query)
        async with self.session.post(self._predict_endpoint, data=data) as resp:
            return await resp.json(encoding='utf8', loads=OCRPrediction.model_validate_json)
