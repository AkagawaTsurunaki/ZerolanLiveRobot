from dataclasses import dataclass

from dataclasses_json import dataclass_json

from common.utils import web_util
from common.abs_pipeline import AbstractPipeline, AbstractModelPrediction, AbstractModelQuery

from common.config.service_config import ServiceConfig

config = ServiceConfig.tts_config


@dataclass_json
@dataclass
class TTSQuery(AbstractModelQuery):
    text: str
    text_language: str
    refer_wav_path: str
    prompt_text: str
    prompt_language: str


@dataclass_json
@dataclass
class TTSPrediction(AbstractModelPrediction):
    wave_data: bytes


class TTSPipeline(AbstractPipeline):

    def __init__(self):
        super().__init__()
        self.predict_url = web_util.urljoin(config.host, config.port, '/tts/predict')
        self.stream_predict_url = web_util.urljoin(config.host, config.port, f'/tts/stream-predict')

    def predict(self, query: TTSQuery) -> TTSPrediction | None:
        return super().predict(query)

    def stream_predict(self, query: TTSQuery):
        return super().stream_predict(query)

    def parse_query(self, query: any) -> dict:
        assert hasattr(query, 'to_dict')
        return query.to_dict()

    def parse_prediction(self, data: bytes) -> TTSPrediction:
        return TTSPrediction(wave_data=data)
