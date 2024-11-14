import json
from http import HTTPStatus
from urllib.parse import urljoin

import requests
from loguru import logger
from zerolan.data.data.asr import ASRModelQuery, ASRModelPrediction, ASRModelStreamQuery

from common.config import ASRPipelineConfig
from pipeline.abs_pipeline import AbstractPipeline


class ASRPipeline(AbstractPipeline):

    def __init__(self, config: ASRPipelineConfig):
        super().__init__(config)
        self.predict_url = urljoin(config.server_url, "/asr/predict")
        self.stream_predict_url = urljoin(config.server_url, '/asr/stream-predict')
        self.state_url = urljoin(config.server_url, '/asr/state')
        self.check_urls()

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

    def parse_query(self, query: ASRModelQuery | ASRModelStreamQuery) -> tuple:
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

    def parse_prediction(self, json_val: any) -> ASRModelPrediction:
        assert hasattr(ASRModelPrediction, "from_json")
        return ASRModelPrediction.from_dict(json.loads(json_val))  # type: ignore[attr-defined]
