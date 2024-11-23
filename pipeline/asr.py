from http import HTTPStatus
from urllib.parse import urljoin

import requests
from loguru import logger
from zerolan.data.pipeline.asr import ASRQuery, ASRPrediction, ASRStreamQuery

from common.config import ASRPipelineConfig
from common.decorator import pipeline_resolve
from pipeline.abs_pipeline import AbstractPipeline


class ASRPipeline(AbstractPipeline):

    def __init__(self, config: ASRPipelineConfig):
        super().__init__(config)
        self.predict_url = urljoin(config.server_url, "/asr/predict")
        self.stream_predict_url = urljoin(config.server_url, '/asr/stream-predict')
        self.state_url = urljoin(config.server_url, '/asr/state')
        self.check_urls()

    @pipeline_resolve()
    def predict(self, query: ASRQuery) -> ASRPrediction | None:
        assert isinstance(query, ASRQuery)
        try:
            files, data = self.parse_query(query)
            response = requests.post(url=self.predict_url, files=files, data=data)

            if response.status_code == HTTPStatus.OK:
                prediction = self.parse_prediction(response.content)
                return prediction

        except Exception as e:
            logger.exception(e)
            return None

    @pipeline_resolve()
    def stream_predict(self, query: ASRStreamQuery):
        files, data = self.parse_query(query)
        response = requests.get(url=self.stream_predict_url, files=files, data=data)

        if response.status_code == HTTPStatus.OK:
            return self.parse_prediction(response.content)
        else:
            response.raise_for_status()

    def parse_query(self, query: ASRQuery | ASRStreamQuery) -> tuple:
        if isinstance(query, ASRQuery):
            files = {"audio": open(query.audio_path, 'rb')}
            data = {"json": query.model_dump_json()}

            return files, data
        elif isinstance(query, ASRStreamQuery):
            files = {"audio": query.audio_data}
            query.audio_data = ""
            data = {"json": query.model_dump_json()}

            return files, data
        else:
            raise ValueError("Can not convert query.")

    def parse_prediction(self, json_val: any) -> ASRPrediction:
        return ASRPrediction.model_validate(json_val)
