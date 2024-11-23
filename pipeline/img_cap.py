from dataclasses import asdict
from urllib.parse import urljoin

from zerolan.data.pipeline.abs_data import AbstractModelQuery
from zerolan.data.pipeline.img_cap import (ImgCapQuery, ImgCapPrediction)

from common.config import ImgCapPipelineConfig
from common.decorator import pipeline_resolve
from pipeline.abs_pipeline import AbstractImagePipeline


class ImgCapPipeline(AbstractImagePipeline):

    def __init__(self, config: ImgCapPipelineConfig):
        super().__init__(config)
        self.predict_url = urljoin(config.server_url, '/img-cap/predict')
        self.stream_predict_url = urljoin(config.server_url, '/img-cap/stream-predict')
        self.state_url = urljoin(config.server_url, '/img-cap/state')
        self.check_urls()

    @pipeline_resolve()
    def predict(self, query: ImgCapQuery) -> ImgCapPrediction | None:
        return super().predict(query)

    @pipeline_resolve()
    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return asdict(query)

    def parse_prediction(self, json_val: str) -> ImgCapPrediction:
        return ImgCapPrediction.model_validate_json(json_val)
