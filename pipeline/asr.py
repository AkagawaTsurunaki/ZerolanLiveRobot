import json
from http import HTTPStatus

import requests
from loguru import logger

from common.abs_pipeline import AbstractPipeline
from common.utils import web_util
from data.asr import ASRModelQuery, ASRModelPrediction, ASRModelStreamQuery


class ASRPipeline(AbstractPipeline):

    def __init__(self, config):
        super().__init__()
        self._model_id = config.model_id
        host, port = config.host, config.port
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
