import os.path
from typing import Tuple, Generator

import requests
from typeguard import typechecked
from zerolan.data.pipeline.asr import ASRQuery, ASRPrediction, ASRStreamQuery

from pipeline.asr.baidu_asr import BaiduASRPipeline
from pipeline.asr.config import ASRPipelineConfig, ASRModelIdEnum
from pipeline.base.base_sync import CommonModelPipeline


class ASRSyncPipeline(CommonModelPipeline):

    def __init__(self, config: ASRPipelineConfig):
        super().__init__(config)
        if config.model_id == ASRModelIdEnum.BaiduASR and config.baidu_asr_config is not None:
            baidu = BaiduASRPipeline(api_key=config.baidu_asr_config.api_key,
                                     secret_key=config.baidu_asr_config.secret_key)
            self.predict = baidu.predict
            self.stream_predict = baidu.stream_predict

    @typechecked
    def predict(self, query: ASRQuery) -> ASRPrediction | None:
        assert isinstance(query, ASRQuery)
        files, data = self.parse_query(query)
        response = requests.post(url=self.predict_url, files=files, data=data)

        response.raise_for_status()
        prediction = self.parse_prediction(response.content)
        return prediction

    @typechecked
    def stream_predict(self, query: ASRStreamQuery, chunk_size: int | None = None) -> Generator[
        ASRPrediction, None, None]:
        assert isinstance(query, ASRStreamQuery)
        files, data = self.parse_query(query)
        response = requests.post(url=self.stream_predict_url, files=files, data=data)
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=chunk_size, decode_unicode=True):
            prediction = self.parse_stream_prediction(chunk)
            yield prediction

    def parse_query(self, query: ASRQuery | ASRStreamQuery) -> Tuple[dict, dict]:
        if isinstance(query, ASRQuery):
            files = None
            if os.path.exists(query.audio_path):
                files = {"audio": open(query.audio_path, 'rb')}
            data = {"json": query.model_dump_json()}

            return files, data
        elif isinstance(query, ASRStreamQuery):
            assert len(query.audio_data) > 0
            files = {"audio": query.audio_data}
            query.audio_data = ""
            data = {"json": query.model_dump_json()}

            return files, data
        else:
            raise ValueError("Can not convert query.")

    def parse_prediction(self, json_val: str) -> ASRPrediction:
        return ASRPrediction.model_validate_json(json_val)

    def parse_stream_prediction(self, chunk: str) -> ASRPrediction:
        return ASRPrediction.model_validate_json(chunk)
