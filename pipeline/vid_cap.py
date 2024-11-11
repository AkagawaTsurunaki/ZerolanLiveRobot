import os
from dataclasses import asdict
from urllib.parse import urljoin

from zerolan.data.abs_data import AbstractModelQuery
from const import get_zerolan_live_robot_core_url
from pipeline.abs_pipeline import AbstractPipeline
from zerolan.data.data.vid_cap import VidCapQuery, VidCapPrediction


class VidCapPipeline(AbstractPipeline):

    def __init__(self):
        super().__init__()

        self.predict_url = urljoin(get_zerolan_live_robot_core_url(), '/vid-cap/predict')

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
