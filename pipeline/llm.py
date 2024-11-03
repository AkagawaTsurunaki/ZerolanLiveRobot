from dataclasses import asdict
from urllib.parse import urljoin

from abs_data import AbstractModelQuery
from const import get_zerolan_live_robot_core_url
from pipeline.abs_pipeline import AbstractPipeline
from zerolan_live_robot_data.data.llm import LLMQuery, LLMPrediction


class LLMPipeline(AbstractPipeline):

    def __init__(self):
        super().__init__()
        self.predict_url = urljoin(get_zerolan_live_robot_core_url(), '/llm/predict')
        self.stream_predict_url = urljoin(get_zerolan_live_robot_core_url(), f'/llm/stream-predict')

    def predict(self, query: LLMQuery) -> LLMPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery):
        return super().stream_predict(query)

    def parse_prediction(self, json_val: any) -> LLMPrediction:
        assert hasattr(LLMPrediction, "from_json")
        return LLMPrediction.from_json(json_val)  # type: ignore[attr-defined]

    def parse_query(self, query: any) -> dict:
        return asdict(query)
