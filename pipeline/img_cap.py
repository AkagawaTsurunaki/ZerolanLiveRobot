from dataclasses import asdict

from abs_data import AbstractModelQuery
from pipeline.abs_pipeline import AbstractImagePipeline
from common.utils import web_util
from zerolan_live_robot_data.data.img_cap import ImgCapQuery, ImgCapPrediction


class ImaCapPipeline(AbstractImagePipeline):

    def __init__(self, config):
        super().__init__()
        self._model_id = config.model_id
        self.predict_url = web_util.urljoin(config.host, config.port, '/img-cap/predict')

    def predict(self, query: ImgCapQuery) -> ImgCapPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return asdict(query)

    def parse_prediction(self, json_val: any) -> ImgCapPrediction:
        assert hasattr(ImgCapPrediction, "from_json")
        return ImgCapPrediction.from_json(json_val)  # type: ignore[attr-defined]
