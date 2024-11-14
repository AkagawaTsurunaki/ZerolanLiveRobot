from dataclasses import asdict
from urllib.parse import urljoin

from zerolan.data.abs_data import AbstractModelQuery
from zerolan.data.data.img_cap import ImgCapQuery, ImgCapPrediction

from common.config import ImgCapPipelineConfig
from pipeline.abs_pipeline import AbstractImagePipeline


class ImgCapPipeline(AbstractImagePipeline):

    def __init__(self, config: ImgCapPipelineConfig):
        super().__init__(config)
        self.predict_url = urljoin(config.server_url, '/img-cap/predict')
        self.stream_predict_url = urljoin(config.server_url, '/img-cap/stream-predict')
        self.state_url = urljoin(config.server_url, '/img-cap/state')
        self.check_urls()

    def predict(self, query: ImgCapQuery) -> ImgCapPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return asdict(query)

    def parse_prediction(self, json_val: any) -> ImgCapPrediction:
        assert hasattr(ImgCapPrediction, "from_json")
        return ImgCapPrediction.from_json(json_val)  # type: ignore[attr-defined]
