from dataclasses import asdict
from urllib.parse import urljoin

from zerolan.data.abs_data import AbstractModelQuery
from zerolan.data.data.llm import LLMQuery, LLMPrediction

from common.config import LLMPipelineConfig
from common.decorator import pipeline_resolve
from pipeline.abs_pipeline import AbstractPipeline

class LLMPipeline(AbstractPipeline):

    def __init__(self, config: LLMPipelineConfig):
        super().__init__(config)
        self.predict_url = urljoin(config.server_url, '/llm/predict')
        self.stream_predict_url = urljoin(config.server_url, f'/llm/stream-predict')
        self.state_url = urljoin(config.server_url, '/llm/state')
        self.check_urls()

    @pipeline_resolve()
    def predict(self, query: LLMQuery) -> LLMPrediction | None:
        return super().predict(query)

    @pipeline_resolve()
    def stream_predict(self, query: AbstractModelQuery):
        return super().stream_predict(query)

    def parse_prediction(self, json_val: any) -> LLMPrediction:
        assert hasattr(LLMPrediction, "from_json")
        return LLMPrediction.from_json(json_val)  # type: ignore[attr-defined]

    def parse_query(self, query: any) -> dict:
        return asdict(query)
