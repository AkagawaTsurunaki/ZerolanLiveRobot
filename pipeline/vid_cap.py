import os
from urllib.parse import urljoin

from zerolan.data.pipeline.abs_data import AbstractModelQuery
from zerolan.data.pipeline.vid_cap import VidCapQuery, VidCapPrediction

from common.config import VidCapPipelineConfig
from common.decorator import pipeline_resolve
from pipeline.abs_pipeline import AbstractPipeline


class VidCapPipeline(AbstractPipeline):

    def __init__(self, config: VidCapPipelineConfig):
        super().__init__(config)
        self.predict_url = urljoin(config.server_url, '/vid-cap/predict')
        self.stream_predict_url = urljoin(config.server_url, '/vid-cap/stream-predict')
        self.state_url = urljoin(config.server_url, '/vid-cap/state')
        self.check_urls()

    @pipeline_resolve()
    def predict(self, query: VidCapQuery) -> VidCapPrediction | None:
        assert os.path.exists(query.vid_path), f"视频路径不存在：{query.vid_path}"
        return super().predict(query)

    @pipeline_resolve()
    def stream_predict(self, query: AbstractModelQuery):
        raise NotImplementedError()

    def parse_prediction(self, json_val: any) -> VidCapPrediction:
        return VidCapPrediction.model_validate(json_val)
