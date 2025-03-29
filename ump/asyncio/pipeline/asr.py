import os
from typing import Dict, BinaryIO, Literal, Generator

from aiohttp import ClientResponse
from typeguard import typechecked
from zerolan.data.pipeline.abs_data import AbstractModelQuery
from zerolan.data.pipeline.asr import ASRQuery, ASRPrediction, ASRStreamQuery

from ump.asyncio.pipeline.base import BaseAsyncPipeline


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


@typechecked
async def stream_generator(response: ClientResponse, chunk_size: int = -1) -> Generator[bytes, None, None]:
    while True:
        chunk = await response.content.read(chunk_size)
        if not chunk:
            break
        yield chunk


ModelID = Literal['iic/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8358-tensorflow1',
'kotoba-tech/kotoba-whisper-v2.0']


class ASRPipeline(BaseAsyncPipeline):
    def __init__(self, model_id: ModelID, base_url: str):
        super().__init__(base_url)
        self._model_id: ModelID = model_id
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
