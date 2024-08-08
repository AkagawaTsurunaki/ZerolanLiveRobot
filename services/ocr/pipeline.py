from dataclasses import dataclass, asdict
from typing import List

from dataclasses_json import dataclass_json

from common.config.service_config import ServiceConfig
from common.utils import web_util
from common.abs_pipeline import AbstractModelQuery, AbstractModelPrediction, AbstractImagePipeline, \
    AbsractImageModelQuery

config = ServiceConfig.ocr_config


@dataclass_json
@dataclass
class OCRQuery(AbsractImageModelQuery):
    pass


@dataclass_json
@dataclass
class Vector2D:
    x: float
    y: float


@dataclass_json
@dataclass
class Position:
    lu: Vector2D  # 左上角
    ru: Vector2D  # 右上角
    rd: Vector2D  # 右下角
    ld: Vector2D  # 左下角


@dataclass_json
@dataclass
class RegionResult:
    position: Position
    content: str
    confidence: float


@dataclass_json
@dataclass
class OCRPrediction(AbstractModelPrediction):
    region_results: List[RegionResult]

    def unfold_as_str(self) -> str:
        result = ""
        for region_result in self.region_results:
            result += region_result.content + "\n"
        return result


class OcrPipeline(AbstractImagePipeline):

    def __init__(self):
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
