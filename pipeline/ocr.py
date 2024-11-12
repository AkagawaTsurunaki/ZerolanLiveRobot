from dataclasses import asdict
from urllib.parse import urljoin

from zerolan.data.abs_data import AbstractModelQuery
from zerolan.data.data.ocr import OCRQuery, OCRPrediction

from common.config.service_config import OCRPipelineConfig as config
from common.decorator import pipeline_enable
from tts.abs_pipeline import AbstractImagePipeline


@pipeline_enable(config.enable)
class OCRPipeline(AbstractImagePipeline):

    def __init__(self):
        super().__init__()
        self.predict_url = urljoin(config.server_url, '/ocr/predict')

    def predict(self, query: OCRQuery) -> OCRPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return asdict(query)

    def parse_prediction(self, json_val: any) -> OCRPrediction:
        assert hasattr(OCRPrediction, "from_json")
        return OCRPrediction.from_json(json_val)  # type: ignore[attr-defined]
