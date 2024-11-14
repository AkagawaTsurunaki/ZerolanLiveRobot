import os
from dataclasses import asdict
from urllib.parse import urljoin

from zerolan.data.abs_data import AbstractModelQuery
from zerolan.data.data.vid_cap import VidCapQuery, VidCapPrediction

from common.config import VidCapPipelineConfig as config
from common.decorator import pipeline_enable
from pipeline.abs_pipeline import AbstractPipeline


class VidCapPipeline(AbstractPipeline):

    @pipeline_enable(config.enable)
    def __init__(self):
        super().__init__()

        self.predict_url = urljoin(config.server_url, '/vid-cap/predict')

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
