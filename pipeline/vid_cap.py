import os
from dataclasses import asdict

from abs_data import AbstractModelQuery
from pipeline.abs_pipeline import AbstractPipeline
from common.utils import web_util
from zerolan_live_robot_data.data.vid_cap import VidCapQuery, VidCapPrediction


class VidCapPipeline(AbstractPipeline):

    def __init__(self, config):
        super().__init__()

        self._model_id = config.model_id
        self.predict_url = web_util.urljoin(config.host, config.port, '/vid-cap/predict')

    def predict(self, query: VidCapQuery) -> VidCapPrediction | None:
        assert os.path.exists(query.vid_path), f"视频路径不存在：{query.vid_path}"
        return super().predict(query)

    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    def parse_query(self, query: any) -> dict:
        return asdict(query)

    def parse_prediction(self, json_val: any) -> VidCapPrediction:
        assert hasattr(VidCapPrediction, "from_json")
        return VidCapPrediction.from_json(json_val)  # type: ignore[attr-defined]
