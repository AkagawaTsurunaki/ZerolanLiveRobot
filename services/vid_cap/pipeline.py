import os
from dataclasses import dataclass, asdict

from dataclasses_json import dataclass_json

from common.utils import web_util
from common.abs_pipeline import AbstractModelQuery, AbstractModelPrediction, AbstractPipeline
from common.config.service_config import ServiceConfig

config = ServiceConfig.vidcap_config


@dataclass_json
@dataclass
class VidCapQuery(AbstractModelQuery):
    vid_path: str


@dataclass_json
@dataclass
class VidCapPrediction(AbstractModelPrediction):
    caption: str
    lang: str


class VidCapPipeline(AbstractPipeline):

    def __init__(self):
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
