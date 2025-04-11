import os
import uuid
from typing import Generator

from typeguard import typechecked
from zerolan.data.pipeline.tts import TTSQuery, TTSPrediction, TTSStreamPrediction

from pipeline.base.base_async import BaseAsyncPipeline, stream_generator, get_base_url
from pipeline.tts.config import TTSPipelineConfig, TTSModelIdEnum


def _parse_tts_query(query: TTSQuery) -> TTSQuery:
    if os.path.exists(query.refer_wav_path):
        query.refer_wav_path = os.path.abspath(query.refer_wav_path).replace("\\", "/")
    return query


class TTSAsyncPipeline(BaseAsyncPipeline):
    def __init__(self, config: TTSPipelineConfig):
        super().__init__(base_url=get_base_url(config.predict_url))
        self._model_id: TTSModelIdEnum = config.model_id
        self._predict_endpoint = "/tts/predict"
        self._stream_predict_endpoint = "/tts/stream-predict"

    @typechecked
    async def predict(self, query: TTSQuery) -> TTSPrediction:
        query = _parse_tts_query(query)
        async with self.session.post(self._predict_endpoint, json=query.model_dump()) as resp:
            data = await resp.content.read()
            return TTSPrediction(wave_data=data, audio_type=query.audio_type)

    @typechecked
    async def stream_predict(self, query: TTSQuery) -> Generator[TTSStreamPrediction, None, None]:
        query = _parse_tts_query(query)
        async with self.session.post(self._stream_predict_endpoint, json=query.model_dump()) as resp:
            last = 0
            id = str(uuid.uuid4())
            idx = 0
            async for chunk in stream_generator(resp):
                last = idx
                yield TTSStreamPrediction(seq=idx,
                                          id=id,
                                          is_final=False,
                                          wave_data=chunk,
                                          audio_type=query.audio_type)
                idx += 1
            yield TTSStreamPrediction(is_final=True, seq=last + 1, audio_type=query.audio_type, wave_data=b'')
