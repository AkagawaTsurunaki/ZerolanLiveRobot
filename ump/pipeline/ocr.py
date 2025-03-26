from typing import List

from pydantic import Field
from requests import Response
from zerolan.data.pipeline.abs_data import AbstractModelQuery
from zerolan.data.pipeline.ocr import OCRQuery, OCRPrediction, RegionResult

from ump.abs_pipeline import AbstractImagePipeline, AbstractPipelineConfig


class OCRPipelineConfig(AbstractPipelineConfig):
    model_id: str = Field(default="paddlepaddle/PaddleOCR", description="The ID of the model used for OCR.")
    predict_url: str = Field(default="http://127.0.0.1:11000/img_cap/predict",
                             description="The URL for OCR prediction requests.")
    stream_predict_url: str = Field(default="http://127.0.0.1:11000/img-cap/stream-predict",
                                    description="The URL for streaming OCR prediction requests.")


class OCRPipeline(AbstractImagePipeline):

    def __init__(self, config: OCRPipelineConfig):
        super().__init__(config)

    def predict(self, query: OCRQuery) -> OCRPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery, chunk_size: int | None = None):
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
