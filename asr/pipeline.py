from dataclasses import dataclass

from common import util
from common.abs_pipeline import AbstractPipeline, AbstractModelResponse, AbstractModelQuery
from config import GlobalConfig


@dataclass
class ASRModelQuery(AbstractModelQuery):
    wav_path: str


@dataclass
class ASRModelResponse(AbstractModelResponse):
    transcript: str


class ASRPipeline(AbstractPipeline):
    def __init__(self, cfg: GlobalConfig):
        super().__init__()
        asr_config = cfg.auto_speech_recognition
        self.model: str = asr_config.models[0].model_name
        host, port = asr_config.host, asr_config.port
        self.predict_url = util.urljoin(host, port, '/asr/predict')

    def predict(self, query: ASRModelQuery) -> ASRModelResponse | None:
        return super().predict(query)

    @staticmethod
    def parse_query_from_json(obj: any) -> ASRModelQuery:
        wav_path = obj['wav_path']
        return ASRModelQuery(wav_path=wav_path)

    @staticmethod
    def parse_response_from_json(obj: any) -> ASRModelResponse:
        transcript = obj['transcript']
        return ASRModelResponse(transcript=transcript)
