from typing import List
from urllib.parse import urljoin

from zerolan.data.pipeline.abs_data import AbstractModelQuery
from zerolan.data.pipeline.ocr import OCRQuery, OCRPrediction, RegionResult

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

    def parse_prediction(self, json_val: str) -> OCRPrediction:
        return OCRPrediction.model_validate_json(json_val)


def avg_confidence(p: OCRPrediction) -> float:
    results = len(p.region_results)
    if results == 0:
        return 0
    confidence_sum = 0
    for region_result in p.region_results:
        confidence_sum += region_result.confidence
    return confidence_sum / results


def stringify(region_results: List[RegionResult]):
    assert isinstance(region_results, list)
    for region_result in region_results:
        assert isinstance(region_result, RegionResult)

    result = ""
    for i, region_result in enumerate(region_results):
        line = f"[{i}] {region_result.content} \n"
        result += line
    return result
