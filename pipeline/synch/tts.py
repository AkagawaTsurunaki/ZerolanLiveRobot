import os.path
import uuid
from http import HTTPStatus

import requests
from zerolan.data.pipeline.tts import TTSQuery, TTSPrediction, TTSStreamPrediction

from ump.abs_pipeline import CommonModelPipeline
from ump.config import TTSPipelineConfig


class TTSPipeline(CommonModelPipeline):

    def __init__(self, config: TTSPipelineConfig):
        super().__init__(config)

    def predict(self, query: TTSQuery) -> TTSPrediction | None:
        assert isinstance(query, TTSQuery)
        if os.path.exists(query.refer_wav_path):
            query.refer_wav_path = os.path.abspath(query.refer_wav_path).replace("\\", "/")
        query_dict = self.parse_query(query)
        response = requests.post(url=self.predict_url, stream=True, json=query_dict)
        if response.status_code == HTTPStatus.OK:
            prediction = TTSPrediction(wave_data=response.content, audio_type=query.audio_type)
            return prediction
        else:
            response.raise_for_status()

    def stream_predict(self, query: TTSQuery, chunk_size: int | None = None):
        assert isinstance(query, TTSQuery)
        if os.path.exists(query.refer_wav_path):
            query.refer_wav_path = os.path.abspath(query.refer_wav_path).replace("\\", "/")
        query_dict = self.parse_query(query)
        response = requests.post(url=self.stream_predict_url, stream=True,
                                 json=query_dict)
        response.raise_for_status()
        last = 0
        id = str(uuid.uuid4())
        for idx, chunk in enumerate(response.iter_content(chunk_size=1024)):
            last = idx
            yield TTSStreamPrediction(seq=idx,
                                      id=id,
                                      is_final=False,
                                      wave_data=chunk,
                                      audio_type=query.audio_type)
        yield TTSStreamPrediction(is_final=True, seq=last + 1, audio_type=query.audio_type, wave_data=b'')

    def parse_query(self, query: any) -> dict:
        return super().parse_query(query)
