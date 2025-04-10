from typing import List

from requests import Response
from zerolan.data.pipeline.ocr import OCRQuery, OCRPrediction, RegionResult

from pipeline.base.base_sync import AbstractImagePipeline
from pipeline.ocr.config import OCRPipelineConfig


class OCRPipeline(AbstractImagePipeline):

    def __init__(self, config: OCRPipelineConfig):
        super().__init__(config)

    def predict(self, query: OCRQuery) -> OCRPrediction | None:
        assert isinstance(query, OCRQuery)
        return super().predict(query)

    def stream_predict(self, query: OCRQuery, chunk_size: int | None = None):
        assert isinstance(query, OCRQuery)
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return super().parse_query(query)

    def parse_prediction(self, response: Response) -> OCRPrediction:
        json_val = response.content
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
