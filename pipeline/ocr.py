from dataclasses import asdict
from urllib.parse import urljoin

from abs_data import AbstractModelQuery
from const import get_zerolan_live_robot_core_url
from data.ocr import OCRQuery, OCRPrediction
from pipeline.abs_pipeline import AbstractImagePipeline


class OcrPipeline(AbstractImagePipeline):

    def __init__(self):
        super().__init__()

        self.predict_url = urljoin(get_zerolan_live_robot_core_url(), '/ocr/predict')

    def predict(self, query: OCRQuery) -> OCRPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return asdict(query)

    def parse_prediction(self, json_val: any) -> OCRPrediction:
        assert hasattr(OCRPrediction, "from_json")
        return OCRPrediction.from_json(json_val)  # type: ignore[attr-defined]
