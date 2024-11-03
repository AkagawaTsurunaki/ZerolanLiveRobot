from dataclasses import asdict

from common.abs_pipeline import AbstractModelQuery, AbstractPipeline
from common.utils import web_util
from zerolan_live_robot_data.data.llm import LLMPrediction, LLMQuery


class LLMPipeline(AbstractPipeline):

    def __init__(self, config: any):
        super().__init__()

        self._model_id = config.model_id
        self.predict_url = web_util.urljoin(config.host, config.port, '/llm/predict')
        self.stream_predict_url = web_util.urljoin(config.host, config.port, f'/llm/stream-predict')

    def predict(self, query: LLMQuery) -> LLMPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery):
        return super().stream_predict(query)

    def parse_prediction(self, json_val: any) -> LLMPrediction:
        assert hasattr(LLMPrediction, "from_json")
        return LLMPrediction.from_json(json_val)  # type: ignore[attr-defined]

    def parse_query(self, query: any) -> dict:
        return asdict(query)
