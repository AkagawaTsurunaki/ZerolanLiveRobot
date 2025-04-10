from typing import Literal

from typeguard import typechecked
from zerolan.data.pipeline.ocr import OCRQuery, OCRPrediction

from pipeline.base.base_async import BaseAsyncPipeline, _parse_imgcap_query

ModelID = Literal['paddlepaddle/PaddleOCR']


class OCRPipeline(BaseAsyncPipeline):
    def __init__(self, model_id: ModelID, base_url: str):
        super().__init__(base_url)
        self._model_id: ModelID = model_id
        self._predict_endpoint = "/ocr/predict"
        self._stream_predict_endpoint = "/ocr/stream-predict"

    @typechecked
    async def predict(self, query: OCRQuery) -> OCRPrediction:
        data = _parse_imgcap_query(query)
        async with self.session.post(self._predict_endpoint, data=data) as resp:
            return await resp.json(encoding='utf8', loads=OCRPrediction.model_validate_json)
