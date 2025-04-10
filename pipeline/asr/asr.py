import os
from typing import Dict, BinaryIO, Generator

from typeguard import typechecked
from zerolan.data.pipeline.abs_data import AbstractModelQuery
from zerolan.data.pipeline.asr import ASRQuery, ASRPrediction, ASRStreamQuery

from pipeline.asr.config import ASRPipelineConfig, ASRModelIdEnum
from pipeline.asynch.base import BaseAsyncPipeline, stream_generator, get_base_url


@typechecked
def _parse_asr_query(query: ASRQuery) -> Dict[str, BinaryIO | str]:
    data = {"json": query.model_dump_json()}
    if os.path.exists(query.audio_path):
        data['audio'] = open(query.audio_path, 'rb')

    return data


@typechecked
def _parse_asr_stream_query(query: ASRStreamQuery) -> Dict[str, BinaryIO | str]:
    assert len(query.audio_data) > 0

    # Only used for converting to json
    class StubASRStreamQuery(AbstractModelQuery):
        is_final: bool
        audio_data: str
        media_type: str
        sample_rate: int
        channels: int

    stub_query = StubASRStreamQuery(
        is_final=query.is_final,
        audio_data="",
        media_type=query.media_type,
        sample_rate=query.sample_rate,
        channels=query.channels,
    )
    data = {"json": stub_query.model_dump_json(), "audio": query.audio_data}

    return data


class ASRPipeline(BaseAsyncPipeline):

    def __init__(self, config: ASRPipelineConfig):
        super().__init__(base_url=get_base_url(config.predict_url))
        self._model_id: ASRModelIdEnum = config.model_id
        self._predict_endpoint = "/asr/predict"
        self._stream_predict_endpoint = "/asr/stream-predict"

    @typechecked
    async def predict(self, query: ASRQuery) -> ASRPrediction:
        data = _parse_asr_query(query)
        async with self.session.post(self._predict_endpoint, data=data) as resp:
            return await resp.json(encoding='utf8', loads=ASRPrediction.model_validate_json)

    @typechecked
    async def stream_predict(self, query: ASRStreamQuery) -> Generator[ASRPrediction, None, None]:
        data = _parse_asr_stream_query(query)
        async with self.session.post(self._stream_predict_endpoint, data=data) as resp:
            async for chunk in stream_generator(resp):
                yield ASRPrediction.model_validate_json(chunk)
