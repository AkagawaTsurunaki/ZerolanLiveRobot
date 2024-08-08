from dataclasses import dataclass, asdict
from typing import Literal

from dataclasses_json import dataclass_json

from common.config.service_config import ServiceConfig
from common.utils import web_util
from common.abs_pipeline import AbstractModelQuery, AbstractModelPrediction, AbstractImagePipeline, \
    AbsractImageModelQuery

config = ServiceConfig.imgcap_config


@dataclass_json
@dataclass
class ImgCapQuery(AbsractImageModelQuery):
    prompt: str = "There"


@dataclass_json
@dataclass
class ImgCapPrediction(AbstractModelPrediction):
    caption: str
    lang: Literal["zh", "en", "ja"]


class ImaCapPipeline(AbstractImagePipeline):

    def __init__(self):
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
