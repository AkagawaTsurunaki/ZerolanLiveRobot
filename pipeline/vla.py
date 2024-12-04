from urllib.parse import urljoin

from zerolan.data.pipeline.vla import ShowUiQuery, ShowUiPrediction

from common.config import ShowUIConfig
from common.decorator import pipeline_resolve
from pipeline.abs_pipeline import AbstractImagePipeline


class ShowUIPipeline(AbstractImagePipeline):
    def __init__(self, config: ShowUIConfig):
        super().__init__(config)
        self.predict_url = urljoin(config.server_url, '/vla/showui/predict')
        self.stream_predict_url = urljoin(config.server_url, '/vla/showui/stream-predict')
        self.state_url = urljoin(config.server_url, '/vla/showui/state')
        self.check_urls()

    @pipeline_resolve()
    def predict(self, query: ShowUiQuery) -> ShowUiPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: ShowUiQuery):
        raise NotImplementedError()

    def parse_prediction(self, json_val: any) -> ShowUiPrediction:
        return ShowUiPrediction.model_validate_json(json_val)
