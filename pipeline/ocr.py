from dataclasses import asdict

from abs_data import AbstractModelQuery
from common.abs_pipeline import AbstractImagePipeline
from common.utils import web_util
from data.ocr import OCRQuery, OCRPrediction


class OcrPipeline(AbstractImagePipeline):

    def __init__(self, config):
        super().__init__()

        self._model_id = config.model_id
        self.predict_url = web_util.urljoin(config.host, config.port, '/ocr/predict')

    def predict(self, query: OCRQuery) -> OCRPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return asdict(query)

    def parse_prediction(self, json_val: any) -> OCRPrediction:
        assert hasattr(OCRPrediction, "from_json")
        return OCRPrediction.from_json(json_val)  # type: ignore[attr-defined]
