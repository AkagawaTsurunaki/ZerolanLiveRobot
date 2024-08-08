import json
from dataclasses import dataclass
from http import HTTPStatus

import requests
from dataclasses_json import dataclass_json
from loguru import logger

from common.utils import web_util
from common.abs_pipeline import AbstractPipeline, AbstractModelPrediction, AbstractModelQuery
from common.config.service_config import ASRServiceConfig as asr_cfg


@dataclass_json
@dataclass
class ASRModelQuery(AbstractModelQuery):
    audio_path: str
    media_type: str = 'wav'
    sample_rate: int = 16000
    channels: int = 1


@dataclass_json
@dataclass
class ASRModelStreamQuery(AbstractModelQuery):
    is_final: bool
    audio_data: bytes
    media_type: str = 'wav'
    sample_rate: int = 16000
    channels: int = 1


@dataclass_json
@dataclass
class ASRModelPrediction(AbstractModelPrediction):
    transcript: str

    def __str__(self):
        return self.transcript


class ASRPipeline(AbstractPipeline):

    def __init__(self):
        super().__init__()
        self._model_id = asr_cfg.model_id
        host, port = asr_cfg.host, asr_cfg.port
        self.predict_url = web_util.urljoin(host, port, '/asr/predict')
        self.stream_predict_url = web_util.urljoin(host, port, '/asr/stream-predict')

    def predict(self, query: ASRModelQuery) -> ASRModelPrediction | None:
        assert isinstance(query, ASRModelQuery)
        try:
            files, data = self.parse_query(query)
            response = requests.post(url=self.predict_url, files=files, data=data)

            if response.status_code == HTTPStatus.OK:
                prediction = self.parse_prediction(response.content)
                return prediction

        except Exception as e:
            logger.exception(e)
            return None

    def stream_predict(self, query: ASRModelStreamQuery):
        files, data = self.parse_query(query)
        response = requests.get(url=self.stream_predict_url, files=files, data=data)

        if response.status_code == HTTPStatus.OK:
            return self.parse_prediction(response.content)
        else:
            response.raise_for_status()

    @staticmethod
    def parse_query(query: ASRModelQuery | ASRModelStreamQuery) -> tuple:
        if isinstance(query, ASRModelQuery):
            files = {"audio": open(query.audio_path, 'rb')}
            data = {"json": query.to_json()}  # type: ignore

            return files, data
        elif isinstance(query, ASRModelStreamQuery):
            files = {"audio": query.audio_data}
            query.audio_data = ""
            data = {"json": query.to_json()}  # type: ignore

            return files, data
        else:
            raise ValueError("无法转换")

    @staticmethod
    def parse_prediction(json_val: any) -> ASRModelPrediction:
        assert hasattr(ASRModelPrediction, "from_json")
        return ASRModelPrediction.from_dict(json.loads(json_val))  # type: ignore[attr-defined]
