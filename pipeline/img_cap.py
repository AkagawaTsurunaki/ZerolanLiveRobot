from dataclasses import asdict
from urllib.parse import urljoin

from zerolan.data.abs_data import AbstractModelQuery
from const import get_zerolan_live_robot_core_url
from pipeline.abs_pipeline import AbstractImagePipeline
from zerolan.data.data.img_cap import ImgCapQuery, ImgCapPrediction


class ImaCapPipeline(AbstractImagePipeline):

    def __init__(self):
        super().__init__()
        self.predict_url = urljoin(get_zerolan_live_robot_core_url(), '/img-cap/predict')

    def predict(self, query: ImgCapQuery) -> ImgCapPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return asdict(query)

    def parse_prediction(self, json_val: any) -> ImgCapPrediction:
        assert hasattr(ImgCapPrediction, "from_json")
        return ImgCapPrediction.from_json(json_val)  # type: ignore[attr-defined]
