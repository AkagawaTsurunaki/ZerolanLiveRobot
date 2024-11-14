from dataclasses import asdict
from urllib.parse import urljoin

from zerolan.data.abs_data import AbstractModelQuery
from zerolan.data.data.img_cap import ImgCapQuery, ImgCapPrediction

from common.config import ImgCapPipelineConfig as config
from common.decorator import pipeline_enable
from pipeline.abs_pipeline import AbstractImagePipeline


class ImgCapPipeline(AbstractImagePipeline):

    @pipeline_enable(config.enable)
    def __init__(self):
        super().__init__()
        self.predict_url = urljoin(config.server_url, '/img-cap/predict')

    def predict(self, query: ImgCapQuery) -> ImgCapPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return asdict(query)

    def parse_prediction(self, json_val: any) -> ImgCapPrediction:
        assert hasattr(ImgCapPrediction, "from_json")
        return ImgCapPrediction.from_json(json_val)  # type: ignore[attr-defined]
