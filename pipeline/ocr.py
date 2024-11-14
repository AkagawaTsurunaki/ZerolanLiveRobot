from dataclasses import asdict
from urllib.parse import urljoin

from zerolan.data.abs_data import AbstractModelQuery
from zerolan.data.data.ocr import OCRQuery, OCRPrediction

from common.config import OCRPipelineConfig
from common.decorator import pipeline_resolve
from pipeline.abs_pipeline import AbstractImagePipeline


class OCRPipeline(AbstractImagePipeline):

    def __init__(self, config: OCRPipelineConfig):
        super().__init__(config)
        self.predict_url = urljoin(config.server_url, '/ocr/predict')
        self.stream_predict_url = urljoin(config.server_url, '/ocr/stream-predict')
        self.state_url = urljoin(config.server_url, '/ocr/state')
        self.check_urls()

    @pipeline_resolve()
    def predict(self, query: OCRQuery) -> OCRPrediction | None:
        return super().predict(query)

    @pipeline_resolve()
    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return asdict(query)

    def parse_prediction(self, json_val: any) -> OCRPrediction:
        assert hasattr(OCRPrediction, "from_json")
        return OCRPrediction.from_json(json_val)  # type: ignore[attr-defined]
