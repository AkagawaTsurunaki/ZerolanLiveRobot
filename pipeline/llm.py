from dataclasses import asdict
from urllib.parse import urljoin

from zerolan.data.abs_data import AbstractModelQuery
from zerolan.data.data.llm import LLMQuery, LLMPrediction

from common.config import LLMPipelineConfig as config
from common.decorator import pipeline_enable
from pipeline.abs_pipeline import AbstractPipeline


class LLMPipeline(AbstractPipeline):

    @pipeline_enable(config.enable)
    def __init__(self):
        super().__init__()
        self.predict_url = urljoin(config.server_url, '/llm/predict')
        self.stream_predict_url = urljoin(config.server_url, f'/llm/stream-predict')

    def predict(self, query: LLMQuery) -> LLMPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery):
        return super().stream_predict(query)

    def parse_prediction(self, json_val: any) -> LLMPrediction:
        assert hasattr(LLMPrediction, "from_json")
        return LLMPrediction.from_json(json_val)  # type: ignore[attr-defined]

    def parse_query(self, query: any) -> dict:
        return asdict(query)
