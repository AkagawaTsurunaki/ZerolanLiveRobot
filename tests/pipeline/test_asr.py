from typing import Generator

import numpy as np
import pytest
from loguru import logger
from zerolan.data.pipeline.asr import ASRQuery, ASRStreamQuery

from common.utils.audio_util import from_bytes_to_np_ndarray
from manager.config_manager import get_config, get_project_dir
from pipeline.asr.asr_async import ASRPipeline
from pipeline.asr.asr_sync import ASRPipeline as ASRPipelineSync

_config = get_config()
_asr = ASRPipeline(_config.pipeline.asr)
_asr_sync = ASRPipelineSync(_config.pipeline.asr)
project_dir = get_project_dir()
audio_path = project_dir.joinpath("tests/resources/tts-test.wav")
_asr_query = ASRQuery(audio_path=str(audio_path), channels=2)


@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    # Needed to work with asyncpg
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


def split_audio(num_chunk: int) -> Generator:
    with open(audio_path, "rb") as f:
        data, samplerate = from_bytes_to_np_ndarray(f.read())
        data = data[:, 0]
        chunk_size = data.shape[0] // num_chunk
        buffer = np.zeros(shape=(1, 1), dtype=np.float32)
        for i in range(num_chunk):
            chunk: np.ndarray = data[i * chunk_size: (i + 1) * chunk_size]
            is_final = i == num_chunk - 1
            buffer = np.append(buffer, chunk)
            query = ASRStreamQuery(is_final=is_final, audio_data=buffer.tobytes(), channels=1, media_type='raw',
                                   sample_rate=samplerate)
            yield query


@pytest.mark.asyncio
async def test_asr():
    prediction = await _asr.predict(_asr_query)
    assert prediction, f"Test failed: No response."
    logger.info(f"ASR result: {prediction.transcript}")
    assert "我是" in prediction.transcript, f"Test failed: Wrong result."


@pytest.mark.asyncio
async def test_asr_stream_predict():
    result = []
    for query in split_audio(num_chunk=4):
        async for prediction in _asr.stream_predict(query):
            assert prediction, f"Test failed: No response."
            logger.info(f"ASR result: {prediction.transcript}")
            result.append(prediction.transcript)
    assert "我是" in result, f"Test failed: Wrong result."


def test_asr_predict_sync():
    prediction = _asr_sync.predict(_asr_query)
    assert prediction, f"Test failed: No response."
    logger.info(f"ASR result: {prediction.transcript}")
    assert "我是" in prediction.transcript, f"Test failed: Wrong result."


def test_asr_stream_predict_sync():
    result = []
    for query in split_audio(num_chunk=4):
        for prediction in _asr_sync.stream_predict(query):
            assert prediction, f"Test failed: No response."
            logger.info(f"ASR result: {prediction.transcript}")
            result.append(prediction.transcript)
    assert "我是" in result, f"Test failed: Wrong result."
